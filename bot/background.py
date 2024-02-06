import datetime
import time

from pytz import timezone

from config import WEATHER_TIME, SCHEDULE_TIME, CABINETS_CLEAR_TIME, cabinets_info
from handlers import send_schedule
from utils import send_weather


def auto_messages_control():
    current_time = datetime.datetime.now(tz=timezone("Europe/Minsk")).strftime("%H%M%S")
    if current_time == WEATHER_TIME:
        send_weather()
        print('[*]WEATHER SENT')
    if current_time == SCHEDULE_TIME and datetime.datetime.now().weekday() == 5:
        send_schedule()
        print('[*]SCHEDULE SENT')
    if current_time == CABINETS_CLEAR_TIME:
        cabinets_info['author'] = {}


def bot_background():
    while True:
        auto_messages_control()
        time.sleep(1)
