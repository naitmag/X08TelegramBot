import datetime
import time

from pytz import timezone

from config import bot, WEATHER_TIME, logger, AUTOWEATHER, AUTOSHUTDOWN, SHUTDOWN_TIMES
from handlers.user_requests import send_weather


def auto_messages_control(current_time: str):
    if AUTOWEATHER and current_time == WEATHER_TIME:
        send_weather()
        logger.info('Weather sent')


def auto_shutdown_control(current_time: str):
    if AUTOSHUTDOWN and current_time in SHUTDOWN_TIMES:
        bot.stop_bot()
        logger.info("Bot autoshutdown")
        exit()


def bot_background():
    while True:
        current_time = datetime.datetime.now(tz=timezone("Europe/Minsk")).strftime("%H%M%S")
        auto_messages_control(current_time)
        auto_shutdown_control(current_time)
        time.sleep(1)
