import json
import random
from datetime import datetime
from telebot import types
import requests
from config import bot, GROUP_ID, CITY, API_WEATHER, START_LESSONS, define_week, define_time, ADMIN_ID
from sql_requests import get_schedule, drop_database, read_txt, get_user, create_user, update_user_level


def send_weather(target: int = None):
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_WEATHER}&units=metric')
    data = json.loads(res.text)
    bot_reply = (f"<b>⛅️Погода {datetime.now().strftime('%d.%m')}:</b>\n"
                 f"\n🌡 Температура: <b>{round(data['main']['temp'])}°C</b>"
                 f"\n🧍 Ощущается как <b>{round(data['main']['feels_like'])}</b>°C"
                 f"\n💧 Влажность: <b>{data['main']['humidity']}%</b>")
    picture_number = random.randint(0, 1)
    file = open(f"../bot/data/img/{data['weather'][0]['main']}/{picture_number}.jpg", 'rb')
    bot.send_photo(target if target is not None else GROUP_ID, file, bot_reply, parse_mode="html")
    file.close()


def detect_user(data: types.Message | types.CallbackQuery) -> str:
    return f"@{data.from_user.username}" if data.from_user.username else data.from_user.first_name


def user_check(message: types.Message):
    userdata = get_user(message.from_user.id)

    if userdata:
        return

    create_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                message.from_user.username)


def check_permissions(message: types.Message, requirement_level: int) -> bool:
    if message.from_user.id == ADMIN_ID:
        return True

    userdata = get_user(message.from_user.id)

    if userdata:
        print(userdata)
        return userdata[5] >= requirement_level

    create_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                message.from_user.username)
    return 0 >= requirement_level


def random_element(args: list) -> str:
    return args[random.randint(0, len(args) - 1)]


def format_schedule(week: int = None, day_of_the_week: int = None) -> str:
    if not week:
        week = ((datetime(2023, 12, 4) - START_LESSONS).days + 1) // 7 + 1
    schedule = get_schedule(week, day_of_the_week)
    if day_of_the_week is None:
        result = f'<b><em>📆 Расписание на неделю {week}</em></b>\n\n'
        day = 0
    else:
        day = day_of_the_week
        result = ''

    result += f"<i><u>{define_week[day]}</u></i>\n"
    for lesson in schedule:
        if lesson[0] != day and day <= 5:
            day += 1
            result += f"\n<i><u>{define_week[day]}</u></i>\n"
        result += f"<b>- {define_time[lesson[1]]}</b> <i>{lesson[2]} {" ".join(lesson[3:4])}</i>\n"
    return result


def format_teacher(data) -> str:
    result_list = []
    for item in data:
        item = f"{" ".join(item[2:4])} {(' '.join(item[6:]))}"
        if item not in result_list:
            result_list.append(item)

    result = "\n".join(result_list)

    return result


def read_database(message: types.Message):
    if check_permissions(message, 5):
        print(f"[S]{detect_user(message)} READING TXT FILE")
        read_txt()


def clear_database(message: types.Message):
    if check_permissions(message, 5):
        print(f"[S]{detect_user(message)} DROPPED DATABASE")
        drop_database()
