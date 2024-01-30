import json
import random
from datetime import datetime

import requests

from config import bot, GROUP_ID, CITY, API_WEATHER, start_lessons
from read import define_time, check_week, define_week


def send_weather():
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_WEATHER}&units=metric')
    data = json.loads(res.text)
    bot_reply = ("<b>Погода на сегодня⛅️:</b>\n"
                 f"\nТемпература: <b>{round(data['main']['temp'])}°C</b>"
                 f"\n(<em>Ощущается как</em> {round(data['main']['feels_like'])}°C)"
                 f"\n<em>Мин.</em> {round(data['main']['temp_min'])}°C, <em>Макс.</em> {round(data['main']['temp_max'])}°C"
                 f"\nВлажность: <b>{data['main']['humidity']}%</b>")
    picture_number = random.randint(0, 1)
    file = open(f"./bot/img/{data['weather'][0]['main']}/{picture_number}.jpg", 'rb')
    bot.send_photo(GROUP_ID, file, bot_reply, parse_mode="html")


def get_schedule(schedule: dict, week: int, day_of_week: int = None) -> str:
    if not week:
        week = ((datetime(2023,12,4) - start_lessons).days+1)//7+1
        print(week)
    if day_of_week is None:
        result = f'<b><em>📆 Расписание на неделю {week}</em></b>\n\n'
        days = schedule.items()
    else:
        result = ''
        days = [list(schedule.items())[day_of_week]]

    for day_i, day in days:
        result += f"<i><u>{define_week[day_i]}</u></i>\n"
        for lessons_i, lessons in day.items():

            for lesson in lessons:

                if lesson == "-":
                    continue
                if check_week(lesson.split()[0], week):
                    lesson = lesson.split()
                    result += f"<b>- {define_time[lessons_i]}</b> <i>{lesson[1]} {lesson[2].replace('_', ' ').capitalize()}</i>\n"
        result += "\n"
    return result
