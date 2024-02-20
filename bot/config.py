from datetime import datetime

import telebot
from telebot import apihelper, StateMemoryStorage

from environs import Env

env = Env()
env.read_env()

TOKEN = env.str('TOKEN')
GROUP_ID = env.int('GROUP_ID')
API_WEATHER = env.str('API_WEATHER')
CITY = env.str('CITY')
WEATHER_TIME = env.str('WEATHER_TIME')
SCHEDULE_TIME = env.str('SCHEDULE_TIME')


START_LESSONS = datetime(2024, 2, 12)

ADMIN_ID = env.int('ADMIN_ID')

admin_mode = True

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(TOKEN, use_class_middlewares=False, state_storage=state_storage)
apihelper.ENABLE_MIDDLEWARE = False

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
    2: "🪩 Среда",
    3: "🌟 Четверг",
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
    6: "кардио",
}

pages = {
    "home":
        {
            0: f"<b>Добро пожаловать в бота <em>208itc</em>!</b>"
               f"\n<em>Персональный бот 208 группы ФКиСКД БГУКИ</em>\n",

            1: f"\n<b>ℹ️Что бот умеет?</b>\n"
               f"\n- <em>Отправлять расписание</em>"
               f"\n- <em>Записывать и присылать кабинеты</em>"
               f"\n- <em>Отправлять список преподавателей</em>"
               f"\n- <em>Присылать погоду с утра</em>"
               f"\n- <em>и многое другое..</em>"
        },

    "help":

        f"⚙️<b><u>Список команд</u></b>"
        f"\n\n<blockquote><b>Получить расписание</b>\n/schedule или /s</blockquote>"
        f"\n- Принимает <em>|неделя| |день|</em> в любом порядке"
        f"\n- Можно указать и только неделю"
        f"\n- Без аргументов отправит текущую неделю"
        f"\n- <b>Пример:</b> <code>/schedule 12 пн</code>"
        f"\n\n<blockquote><b>Управление кабинетами</b>\n/cabinets или /c или <u>каб</u></blockquote>"
        f"\n- Принимает <em>|кабинет| |кабинет|</em>.."
        f"\n- Максимальное количество кабинетов : 4"
        f"\n- Без аргументов отправит список кабинетов"
        f"\n- <b>Пример:</b> <code>/cabinets 508 800а 507/800</code>"
        f"\n\n<blockquote><b>Добавить занятие</b>\n/add</blockquote>"
        f"\n- Принимает <em>|период или неделя| |день недели| |номер пары| |название_пары|</em>.."
        f"\n- Опционально <em>|тип пары| |преподаватель| </em>"
        f"\n- Доступ имеют определенные пользователи"
        f"\n- <b>Пример:</b> <code>/add 2-14 ср 4 компьютерная_графика сем. иванов</code>"
        f"\n\n<blockquote><b>Узнать преподавателя</b>\n/teacher или /t</blockquote>"
        f"\n- Принимает <em>|название_предмета|</em> или <em>|фамилия|</em>"
        f"\n- Покажет список предметов и преподавателей"
        f"\n- <b>Пример:</b> <code>/teacher информационные_технологии</code>"
        f"\n\n<blockquote><b>Получить погоду</b>\n/weather или /w</blockquote>"
        f"\n- Отправит погоду на данный момент в городе Минск"
        f"\n- <b>Пример:</b> <code>/weather</code>"
        f"\n\n<blockquote><b>Случайный элемент</b>\n/random или /r</blockquote>"
        f"\n- Принимает <em>|элемент1| |элемент2|</em>.."
        f"\n- Случайно выберет один элемент"
        f"\n- Отлично подойдет для распределения семинаров"
        f"\n- <b>Пример:</b> <code>/random @naitmag @BotFather</code>"
        f"\n\n<blockquote><b>Команды администратора</b>\n/admin</blockquote>"
        f"\n- Список команд для администратора"
        f"\n- Команды для тех. части бота",

    "contacts":

        f"📇<b>Контакты:</b>\n"

        f"\n📷 <i><b>Instagram:</b></i>"
        f"\n- <a href='https://www.instagram.com/itinculture/'>Кафедра ИТК</a>"
        f"\n- <a href='https://www.instagram.com/208itk'>Группа 208</a>"
        f"\n\n👤 <i><b>Обратная связь</b></i>:"
        f"\n- <a href='https://t.me/naitmag'>Создатель бота</a>",

    "admin":

        f"<b><u>🔐 Команды администратора</u></b>"
        f"\n\n<blockquote><b>Загрузить расписание</b>\n/read</blockquote>"
        f"\n- Заносит расписание в базу данных"
        f"\n\n<blockquote><b>Очистить расписание</b>\n/drop</blockquote>"
        f"\n- Полностью очищает расписание"
        f"\n- Будьте полностью уверены перед отправкой"
        f"\n\n<blockquote><b>Назначить права</b>\n/set</blockquote>"
        f"\n- Устанавливает роль для участника"
        f"\n- Позволяет закрыть доступ участнику"
        f"\n\n<blockquote><b>Узнать роль</b>\n/perm</blockquote>"
        f"\n- Показывает роль участника"
        f"\n\n<blockquote><b>Узнать ID</b>\n/id</blockquote>"
        f"\n- Позволяет узнать телеграм ID аккаунта"
        f"\n- Доступно всем участникам",

    "roles":

        f"<b>🧙🏼 <u>Роли</u></b>\n"
        f"\n<b>Роли</b> - <i>возможность разделить обязанности среди участников, "
        f"открывает или закрывает доступ к возможностям бота.</i>"
        f"\n\n<blockquote><b>Администратор 🔐</b></blockquote>"
        f"\n- Доступны все возможности бота"
        f"\n\n<blockquote><b>Староста 👨‍🏫</b></blockquote>"
        f"\n- Позволяет добавлять и удалять занятия"
        f"\n- Может пользоваться /random в группе"
        f"\n\n<blockquote><b>Редактор 📝</b></blockquote>"
        f"\n- Позволяет добавлять и удалять занятия"
        f"\n\n<blockquote><b>Уровень 3️⃣</b></blockquote>"
        f"\n- <i>В разработке..</i>"
        f"\n\n<blockquote><b>Одногруппник 👨‍🎓</b></blockquote>"
        f"\n- Позволяет запрашивать расписание"
        f"\n\n<blockquote><b>Пользователь 👤</b></blockquote>"
        f"\n- Обычный пользователь"
        f"\n\n<blockquote><b>Заблокирован 🚫</b></blockquote>"
        f"\n- Закрывает доступ к общим командам"
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
            "понедельник": (35, "Опять понедельник😫"),
            "суббот": (35, "В субботу спать надо😴"),
            "блять": (40, "Маты это плохо😳"),
            "орлова": (35, "Катя топ💅🏼"),
            "🤡": (50, "🤡"),
            "с днём": (50, "Поздравляем!🎉"),
            "арбуз": (40, "Твой папа карапуз🍉"),
            "староста": (40, "Староста крутая😋 (меня заставили это сказать)")

        },
    'photo':
        (5, ["Красивое😍", "Очень красиво☺️", "Прекрасное фото🤤"])

}
