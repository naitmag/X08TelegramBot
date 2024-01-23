import datetime
import json
import time

import requests
from pytz import timezone

from config import bot, GROUP_ID, CITY, API_WEATHER


def send_weather():
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_WEATHER}&units=metric')
    data = json.loads(res.text)
    bot_reply = ("<b>Погода на сегодня:⛅️</b>"
                 f"\nТемпература: <b>{round(data['main']['temp'])}°C</b> (<em>Ощущается как</em> {round(data['main']['feels_like'])}°C)"
                 f"\n<em>Мин.</em> {round(data['main']['temp_min'])}°C, <em>Макс.</em> {round(data['main']['temp_max'])}°C"
                 f"\nВлажность: <b>{data['main']['humidity']}%</b>")
    file = open(f"./img/{data['weather'][0]['main']}.jpg", 'rb')
    bot.send_photo(GROUP_ID, file, bot_reply, parse_mode="html")


def bot_background():
    while True:
        if timezone('Europe/Minsk').localize(datetime.datetime.now()).strftime("%H%M%S") == "213120":
            send_weather()
        time.sleep(1)
