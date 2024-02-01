import datetime
import time

from pytz import timezone

from config import WEATHER_TIME, SCHEDULE_TIME, CABINETS_CLEAR_TIME, cabinets_info
from utils import send_weather, send_schedule


def bot_background():
    while True:
        if datetime.datetime.now(tz=timezone("Europe/Minsk")).strftime("%H%M%S") == WEATHER_TIME:
            send_weather()
            print('[*]WEATHER SENT')
        if (datetime.datetime.now(tz=timezone("Europe/Minsk")).strftime("%H%M%S") == SCHEDULE_TIME
                and datetime.datetime.now().weekday() == 6):
            send_schedule()
            print('[*]SCHEDULE SENT')
        if datetime.datetime.now(tz=timezone("Europe/Minsk")).strftime("%H%M%S") == CABINETS_CLEAR_TIME:
            cabinets_info['author'] = {}
        time.sleep(1)
