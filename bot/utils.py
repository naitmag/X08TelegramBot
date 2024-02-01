import json
import random
from datetime import datetime
from telebot import types
import requests

from config import bot, GROUP_ID, CITY, API_WEATHER, START_LESSONS, schedule as sched, PERMISSIONS
from read import define_time, check_week, define_week


def send_weather(target: int = None):
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_WEATHER}&units=metric')
    data = json.loads(res.text)
    bot_reply = (f"<b>⛅️Погода {datetime.now().strftime('%d.%m')}:</b>\n"
                 f"\n🌡 Температура: <b>{round(data['main']['temp'])}°C</b>"
                 f"\n🧍 Ощущается как <b>{round(data['main']['feels_like'])}</b>°C"
                 f"\n💧 Влажность: <b>{data['main']['humidity']}%</b>")
    picture_number = random.randint(0, 1)
    file = open(f"./bot/img/{data['weather'][0]['main']}/{picture_number}.jpg", 'rb')
    bot.send_photo(target if target is not None else GROUP_ID, file, bot_reply, parse_mode="html")
    file.close()


def get_schedule(schedule: dict, week: int = None, day_of_week: int = None) -> str:
    if not week:
        week = ((datetime(2023, 12, 4) - START_LESSONS).days + 1) // 7 + 1
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


def send_schedule(week: int = None, day_of_week: int = None, target: int = None):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("◀️", callback_data="back")
    button2 = types.InlineKeyboardButton("▶️", callback_data="next")
    markup.row(button1, button2)
    bot.send_message(target if target else GROUP_ID, get_schedule(sched, week, day_of_week), parse_mode='html',
                     reply_markup=markup)


def add_lesson(week: str, day_of_week: int, lesson_number: int, name: str, teacher: str = "-",
               lesson_type: str = 'доп'):
    day_of_week %= 7
    lesson_number %= 5

    if sched[day_of_week].get(lesson_number) is None:
        sched[day_of_week][lesson_number] = []

    sched[day_of_week][lesson_number].append(f"{week} {lesson_type} {name} {teacher}")


def detect_user(message) -> str:
    return f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name


def check_permissions(user_id: int, requirement_level: int) -> bool:
    return int(PERMISSIONS[f"{user_id}"]) if PERMISSIONS.get(f"{user_id}") else 0 >= requirement_level


def random_element(args: list) -> str:
    return args[random.randint(0, len(args) - 1)]


def teachers_by_day(day_of_week) -> str:
    days = [list(sched.items())[day_of_week]]
    result = []

    for day_i, day in days:
        for lessons_i, lessons in day.items():
            for lesson in lessons:
                field = (f"{lesson.split()[1]} "
                         f"<em>{lesson.split()[2][0:12].capitalize().replace('_', ' ')}{".." if len(lesson.split()[2]) > 15 else ''}</em> "
                         f"<b>{' '.join(lesson.split()[3:])}</b>")
                if field not in result:
                    result.append(field)
    result.sort()
    return f"<u>{define_week[day_of_week]}</u>\n{'\n'.join(result)}"
