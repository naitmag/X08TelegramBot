from datetime import datetime
from logger import logger
import telebot
from environs import Env
from telebot import apihelper, StateMemoryStorage

from middleware import ExceptionHandler

env = Env()
env.read_env()

TOKEN = env.str('TOKEN')
GROUP_ID = env.int('GROUP_ID')
API_WEATHER = env.str('API_WEATHER')
CITY = env.str('CITY')
AUTOWEATHER = env.bool('AUTOWEATHER')
WEATHER_TIME = env.str('WEATHER_TIME')
AUTOSHUTDOWN = env.bool('AUTOSHUTDOWN')
SHUTDOWN_TIMES = env.list('SHUTDOWN_TIMES')
LOGGING_LEVEL = env.str('LOGGING_LEVEL')
START_LESSONS = datetime(2024, 2, 12)

ADMIN_ID = env.int('ADMIN_ID')
admin_mode = True

exception_handler = ExceptionHandler(logger)
state_storage = StateMemoryStorage()

bot = telebot.TeleBot(TOKEN, use_class_middlewares=True, state_storage=state_storage,
                      exception_handler=exception_handler)
apihelper.ENABLE_MIDDLEWARE = True

cabinets_info = {"cabinets": [], "author": 'неизвестно'}

days = {
    0: "пн",
    1: "вт",
    2: "ср",
    3: "чт",
    4: "пт",
    5: "сб",
    "пн": 0,
    "вт": 1,
    "ср": 2,
    "чт": 3,
    "пт": 4,
    "сб": 5,
}

define_week = {
    0: "🫨 Понедельник",
    1: "☕️ Вторник",
    2: "📎 Среда",
    3: "🎧 Четверг",
    4: "🍻 Пятница",
    5: "🛌 Суббота"
}

define_time = {
    0: "8:00",
    1: "9:35",
    2: "11:10",
    3: "13:00",
    4: "14:35",
    5: "16.10"
}

define_lesson_type = {
    0: "л.",
    1: "сем.",
    2: "пр.",
    3: "лаб.",
    4: "спорт.",
    5: "кардио",
    6: "сил.",
    7: "доп",
}

roles = {
    -1: "Заблокирован 🚫",
    0: "Пользователь 👤",
    1: "Одногруппник 👨‍🎓",
    2: "Уровень 3️⃣",
    3: "Редактор 📝",
    4: "Староста 👨‍🏫",
    5: "Администратор 🔐"
}

events = {
    'text':
        {
            "понедельник": (40, "Опять понедельник😫"),
            "суббот": (40, "В субботу спать надо😴"),
            "блять": (50, "Маты это плохо😳"),
            "орлова": (50, "Катя топ💅🏼"),
            "🤡": (100, "🤡"),
            "с днём": (100, "Поздравляем!🎉"),
            "арбуз ": (50, "Твой папа карапуз🍉"),
            "староста": (35, "Староста крутая😋 (меня заставили это сказать)")

        },
    'photo':
        (3, ["Красивое😍", "Очень красиво☺️", "Прекрасное фото🤤"])

}
