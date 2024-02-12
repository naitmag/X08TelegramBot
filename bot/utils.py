import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import requests
from pytz import timezone
from telebot import types

import config
from config import bot, GROUP_ID, CITY, API_WEATHER, START_LESSONS, define_week, define_time, ADMIN_ID
from sql_requests import get_schedule, drop_database, read_txt, get_user


def send_weather(target: int = None):
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_WEATHER}&units=metric')
    data = json.loads(res.text)
    bot_reply = (f"<b>⛅️Погода {datetime.now(tz=timezone("Europe/Minsk")).strftime('%H:%M')}</b>\n"
                 f"\n🌡 Температура: <b>{round(data['main']['temp'])}°C</b>"
                 f"\n🧍 Ощущается как <b>{round(data['main']['feels_like'])}</b>°C"
                 f"\n💧 Влажность: <b>{data['main']['humidity']}%</b>")
    picture_number = random.randint(0, 1)
    path = f"{Path(__file__).parent.resolve()}/data/img/{data['weather'][0]['main']}/{picture_number}.jpg"

    file = open(path, 'rb')
    bot.send_photo(target if target is not None else GROUP_ID, file, bot_reply, parse_mode="html")
    file.close()


def detect_user(data: types.Message | types.CallbackQuery) -> str:
    return data.from_user.username if data.from_user.username else data.from_user.first_name


def detect_chat(data: types.Message) -> str:
    return data.chat.title[:15] if data.chat.title else "Private"


def check_permissions(message: types.Message, requirement_level: int) -> bool:
    if config.admin_mode and message.from_user.id == ADMIN_ID:
        return True

    userdata = get_user(message.from_user.id)

    access = userdata[5] >= requirement_level

    if not access and type(message) is types.Message:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])

    return access


def random_element(args: list) -> str:
    return args[random.randint(0, len(args) - 1)]


def format_schedule(week: int = None, day_of_the_week: int = None) -> str:
    if not week:
        week = max(((datetime.now() - START_LESSONS).days + 1) // 7 + 1, 1)

    schedule = get_schedule(week, day_of_the_week)

    result = f'<b><em>📆 Расписание на неделю {week}</em></b>\n\n'

    if not schedule:
        result += "<b> - Нет занятий</b>"
        return result
    if day_of_the_week is None:
        day = schedule[0][0]
    else:
        day = day_of_the_week
        result = ''

    monday_day = START_LESSONS + timedelta(weeks=week - 1)
    result += f"<i><u>{define_week[day]}</u> {(monday_day + timedelta(days=day)).strftime('%d.%m')}</i>\n"
    for lesson in schedule:

        if lesson[0] != day and day < 5:
            day = lesson[0]

            result += (f"\n<i><u>{define_week[lesson[0]]}</u> "
                       f"{(monday_day + timedelta(days=lesson[0])).strftime('%d.%m')}</i>\n")

        result += f"<b>- {define_time[lesson[1]]}</b> <i>{lesson[2]} {' '.join(lesson[3:4])}</i>\n"

    return result


def format_teacher(data) -> str:
    result_list = []
    for item in data:
        item = f" - <i><b>{' '.join(item[2:4])}</b></i> :\n {(' '.join(item[6:]))}"
        if item not in result_list:
            result_list.append(item)
    result_list.sort()
    result = "\n".join(result_list)

    return result


def read_database(message: types.Message):
    print(f"[A]{detect_user(message)} READING TXT FILE")
    read_txt()


def clear_database(message: types.Message):
    print(f"[A]{detect_user(message)} DROPPED DATABASE")
    drop_database()
