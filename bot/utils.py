import json
import random
from datetime import datetime, timedelta

import requests
from pytz import timezone
from telebot import types

import config
from config import bot, CITY, API_WEATHER, START_LESSONS, define_week, define_time, ADMIN_ID, logger
from sql_requests import get_schedule, drop_database, read_txt, get_user


def get_weather() -> str:
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_WEATHER}&units=metric')
    data = json.loads(res.text)
    result = (f"<b>⛅️Погода {datetime.now(tz=timezone('Europe/Minsk')).strftime('%H:%M')}</b>\n"
              f"\n🌡 Температура: <b>{round(data['main']['temp'])}°C</b>"
              f"\n🧍 Ощущается как <b>{round(data['main']['feels_like'])}</b>°C"
              f"\n💧 Влажность: <b>{data['main']['humidity']}%</b>")
    return result


def detect_user(data: types.Message | types.CallbackQuery) -> str:
    return f"@{data.from_user.username}" if data.from_user.username else data.from_user.first_name


def detect_chat(data: types.Message | types.CallbackQuery) -> str:
    if isinstance(data, types.CallbackQuery):
        data = data.message

    return data.chat.type[0].upper()


def check_permissions(querry: types.Message | types.CallbackQuery, requirement_level: int, hiden_mode=False) -> bool:
    if config.admin_mode and querry.from_user.id == ADMIN_ID:
        return True

    userdata = get_user(querry.from_user.id)

    access = userdata[5] >= requirement_level

    if not access:
        action = querry.text if isinstance(querry, types.Message) else querry.data
        log_info(querry, f"don't have permissons {requirement_level}: {action}")
        if not hiden_mode:
            if isinstance(querry, types.Message):
                bot.reply_to(querry, "❌<b>У вас нет прав.</b>\n<em>Подробнее: /roles</em>", parse_mode='html')
            else:
                bot.answer_callback_query(querry.id, "❌У вас нет прав.\nПодробнее: /roles", show_alert=True)

    return access


def random_element(args: list) -> str:
    return args[random.randint(0, len(args) - 1)]


def format_schedule(week: int = None, day_of_the_week: int = None) -> str:
    if not week:
        week = get_current_week()

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
    if result_list:
        result = "\n".join(result_list)
    else:
        result = "<b> - Нет результатов. </b>"

    return result


def read_database(message: types.Message):
    log_info(message)
    read_txt()


def clear_database(message: types.Message):
    log_warn(message, 'DROPPED DATABASE')
    drop_database()


def log_info(querry: types.Message | types.CallbackQuery, action: str = None):
    querry_type = str(type(querry)).split("'")[1].split('.')[2][0]
    if not action:
        action = querry.text if isinstance(querry, types.Message) else querry.data
    logger.info(f"{detect_chat(querry)}-{querry_type} | {detect_user(querry)} {action}")


def log_warn(querry: types.Message | types.CallbackQuery, action: str):
    logger.warning(f"{detect_user(querry)} {action}")


def get_current_week():
    return max(((datetime.now() - START_LESSONS).days + 1) // 7 + 1, 1)
