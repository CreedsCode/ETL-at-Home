# from asyncio import tasks
# from datetime import timedelta
# from airflow import DAG
# from airflow.operators.python_operator import PyhtonOperator
# from airflow.utils.dates import days_ago

# default_args = {
#   "owner": "airflow",
#   "depends_on_past": False,
#   "start_date": days_ago(0,0,0,0,0),
#   "emal": ["funnymail1@pog.com", "funnymail2@pog.com"],
#   "email_on_failure": False,
#   "email_on_retry": False,
#   "retries": 1,
#   "retry_delay": timedelta(minutes=1)
# }

# dag = DAG(
#   "spotify_dag",
#   default_args="Our first DAG with ETL process"
# )

# def just_a_function():
#   print("I'm going to show you something :)")
  
# run_etl = PyhtonOperator(
#   task_id="whole_spotify_etl",
#   python_callable=just_a_function,
#   dag=dag
# )

# run_etl

import requests
req = requests.get('https://api.spotify.com/v1/me/top/tracks', auth='Bearer BQBSSBuWxvmYVFfYQFkK492ROf5JvEqJm506gGTT_M0F1hc3M9eO2vSwtUDKubbAem-EOlNYGjcq3HB7mfVphBMWfP98orYiUvhfC0oxEQkxdVOmdQxLXkPpbp-BRx4A4YhojqcdVeKpkR26CEF_Y2yf8Kcmd8GvbbSpbqzjKcEBIKJ2HkqRUZ5bOcFRzmx0KNHfFrOw3APDejaMoBXKroA4jS3EPe3G0Rg7nco_YQlVMBDFyLBw7InAo-onFh75c0WkKizyHCLWPGjNHEo', headers={
  'Content-Type': 'application/json',
  'Accept': 'application/json'
})

print(req.json())
