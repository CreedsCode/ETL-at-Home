from urllib import response
from dotenv import load_dotenv
from matplotlib.font_manager import json_load
from stravalib import Client
import os
import json
import itertools
import pandas as pd

def init_strava_secrets():
    return {
        "client_key": "ab8b4a41566663ec5ffa560e53c25d6fc8807580",
        "access_token": os.environ.get("ACCESS_TOKEN"),
        "refresh_token": os.environ.get("REFRESH_TOKEN"),
        "client_id": "60192"
        }

def main():
    secrets = init_strava_secrets()

    client = Client()
    # url = client.authorization_url(client_id=secrets["client_id"],
    #                            redirect_uri='http://127.0.0.1:5000/authorization')
    # print(url)
    response_url = "http://127.0.0.1:5000/authorization?state=&code=807b9ea3c45d70a73fa0394247b7d862a4a3462b&scope=read,activity:read"
    code = response_url.split("&")[1].split("=")[1]
    client_exchange_response = client.exchange_code_for_token(client_id=secrets["client_id"],client_secret=secrets["client_key"],code=code)
    print(client_exchange_response)
    client_exchange_response = {}
    with open('.strava_tmp') as d:
        client_exchange_response = json.load(d)
    # get all activities
    client = Client(access_token=client_exchange_response["access_token"])
    print(client.get_athlete())
    activities = client.get_activities()
    print(activities)
    records = []
    for activity in activities:
        print(activity)
        record = {
            "Name": activity.name,
            "Tag": f"'{activity.start_date_local.day}.{activity.start_date_local.month}.{activity.start_date_local.year}'",
            "Zeit": f"{activity.start_date_local.hour}:{activity.start_date_local.minute}:{activity.start_date_local.second}",
            "Typ": activity.type,
            "Durschn. Trittfrequenz": activity.average_cadence,
            "Durschn. Herzfrequenz": activity.average_heartrate,
            "Höchste. Herzfrequenz": activity.max_heartrate,
            "Durschn. Geschwindigkeit (Meter/s)": activity.average_speed.num,
            "Höchste. Geschwindigkeit (Meter)": activity.max_speed.num,
            "Durschn. Temperatur": activity.average_temp,
            "Durschn. Leistung (Watt)": activity.average_watts,
            "Kalorien": activity.calories,
            "Distanz (Meter)": activity.distance,
            "Gesamtzeit": activity.elapsed_time.seconds,
            "Bewegungszeit": activity.moving_time.seconds,
            "Bewegungszeit": activity.moving_time.seconds,
            "upload_id": activity.upload_id,
            "guid": activity.guid
            }
        # print(record)
        records.append(record)
    # group them:
    record_each_day = [list(g) for k, g in itertools.groupby(records, key=lambda d: d["Tag"])]
    print(record_each_day)
    # yeet them to xlsx
    for day in record_each_day:
        df = pd.DataFrame.from_dict(day)
        df.to_excel(f"StravaExports/Strava-Export-{day[0]['Tag']}.xlsx",index=False)


if __name__ == "__main__":
    main()