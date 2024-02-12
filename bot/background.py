import datetime
import time

from pytz import timezone

from config import WEATHER_TIME, SCHEDULE_TIME
from handlers import send_schedule
from utils import send_weather


def auto_messages_control():
    current_time = datetime.datetime.now(tz=timezone("Europe/Minsk")).strftime("%H%M%S")
    if current_time == WEATHER_TIME:
        send_weather()
        print('[*]Weather sent')
    if current_time == SCHEDULE_TIME and datetime.datetime.now().weekday() == 5:
        send_schedule()
        print('[*]Schedule sent')


def bot_background():
    while True:
        auto_messages_control()
        time.sleep(1)
