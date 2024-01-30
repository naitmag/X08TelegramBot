import datetime
import time

from pytz import timezone

from config import WEATHER_TIME
from utils import send_weather


def bot_background():
    while True:
        if datetime.datetime.now(tz=timezone("Europe/Minsk")).strftime("%H%M%S") == WEATHER_TIME:
            send_weather()
        time.sleep(1)
