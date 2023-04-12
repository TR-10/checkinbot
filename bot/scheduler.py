from apscheduler.schedulers.background import BackgroundScheduler
import travelplanner as tp
from time import sleep
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

scheduler = BackgroundScheduler()

def checkin_later(flight):
    try:
        tp.open_tp_home()
        tp.checkin(flight)
        tp.closeBrowser()
    except:
        tp.closeBrowser()
        pass
    


def checkin_now(flight):
    try:
        print('here')
        tp.checkin(flight)
        tp.closeBrowser()
    except:
        print("exception in checkin likely flight is already checked in")
        tp.closeBrowser()

@scheduler.scheduled_job('interval', id='check_flight_info', hours=1)
def check_info():
    try:
        print('running')
        tp.open_tp_home()
        info = tp.get_flights_info()
        print(info)
        for flight in info:
            if(datetime.now() >= datetime.strptime(flight['checkin_time'],'%Y-%m-%d %H:%M:%S.%f')):
                print('true')
                checkin_now(flight["flight_name"])
            else:
                scheduler.add_job(checkin_later(flight["flight_name"]),'date',run_date = flight['checkin_time'], args=['text'],id=f'{flight["flight_name"]}_{flight["recordLocator"]}')
        tp.closeBrowser()

    except Exception:
        tp.closeBrowser()
    # except:
    #     pass
scheduler.start()
# check_info()
while True:
    scheduler.print_jobs()
    sleep(1)
