import datetime as dt
from datetime import timedelta
import ftplib
from lib2to3.pgen2.token import VBAREQUAL
from pendulum import yesterday
from stravalib import Client
import itertools
import pandas as pd
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import DAG, TaskInstance
from datetime import datetime
from airflow.providers.sftp.operators.sftp import SFTPOperator
from airflow.providers.sftp.sensors.sftp import SFTPSensor
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from csv import reader
import pandas as pd
from airflow.contrib.hooks.sftp_hook import SFTPHook
import airflow.providers.ftp 
from airflow.contrib.hooks.ssh_hook import SSHHook
import requests
from requests.structures import CaseInsensitiveDict
from airflow.models import Variable
from airflow.providers.ftp.hooks.ftp import FTPHook
from airflow.exceptions import AirflowSkipException

def _refresh_token(task_instance: TaskInstance, **kwargs):
    
    url = "https://www.strava.com/api/v3/oauth/token"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    client_id = 60192
    client_secret = Variable.get("strava_client_secret")
    
    refresh_token = Variable.get("strava_refresh_token")
    
    
    data = f"client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token&refresh_token={refresh_token}"


    resp = requests.post(url, headers=headers, data=data)
    resp_data = resp.json()
    Variable.update(key="strava_refresh_token", value=resp_data["refresh_token"])
    print("done")
    print(resp_data)
    return resp_data["access_token"]


def _extract(task_instance: TaskInstance, **kwargs):
    access_token = task_instance.xcom_pull(task_ids=["refresh_token"])[0]
    client = Client(access_token=access_token)
    
    # # yesterday
    # today = dt.datetime.now() - timedelta(days=1)
    today = dt.datetime.now()
    activities = client.get_activities()

    todays_activities = []
    for activity in activities:
        if activity.start_date.date() == today.date():
            print("same day")
            todays_activities.append(activity)

    if len(todays_activities) == 0:
        print("No records for today")
        raise AirflowSkipException
    
    records = []
    for entry in todays_activities:
        record = {
            "Name": entry.name,
            "Tag": f"'{entry.start_date_local.day}.{entry.start_date_local.month}.{entry.start_date_local.year}'",
            "Zeit": f"{entry.start_date_local.hour}:{entry.start_date_local.minute}:{entry.start_date_local.second}",
            "Typ": entry.type,
            "Durschn. Trittfrequenz": entry.average_cadence,
            "Durschn. Herzfrequenz": entry.average_heartrate,
            "Höchste. Herzfrequenz": entry.max_heartrate,
            "Durschn. Geschwindigkeit (Meter/s)": entry.average_speed.num,
            "Höchste. Geschwindigkeit (Meter)": entry.max_speed.num,
            "Durschn. Temperatur": entry.average_temp,
            "Durschn. Leistung (Watt)": entry.average_watts,
            "Kalorien": entry.calories,
            "Distanz (Meter)": entry.distance,
            "Gesamtzeit": entry.elapsed_time.seconds,
            "Bewegungszeit": entry.moving_time.seconds,
            "Bewegungszeit": entry.moving_time.seconds,
            "upload_id": entry.upload_id
            }
        records.append(record)
        
    df = pd.DataFrame.from_dict(records)
    filename = "Strava-Export-" + records[0]['Tag'] + ".xlsx"
    df.to_excel("/tmp/" + filename,index=False)
    return filename
    
def _upload(task_instance: TaskInstance, **kwargs):
    filename = task_instance.xcom_pull(task_ids='extract')
            
    ftp_hook = FTPHook(ftp_conn_id="airflow_ftp")
    
    ftp_hook.store_file(
                        remote_full_path = f"/strava_exporte/{filename}",
                        local_full_path_or_buffer= f"/tmp/{filename}"
                        )
    
default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2022, 4, 18, 10, 00, 00)
}

with DAG('strava_shit',
         default_args=default_args,
         ) as dag:

    refresh_token = PythonOperator(task_id='refresh_token',
                                 python_callable=_refresh_token)
    
    extract_and_transform = PythonOperator(task_id='extract',
                                 python_callable=_extract)

    upload_file = PythonOperator(task_id='upload',
                                 python_callable=_upload)

refresh_token >> extract_and_transform >> upload_file