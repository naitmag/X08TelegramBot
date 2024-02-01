import time

from telebot import types

from config import cabinets_info, bot, schedule, ADMIN_ID
from utils import send_schedule, get_schedule, send_weather, add_lesson, detect_user, check_permissions, random_element, \
    teachers_by_day
from read import define_time

days = ("пн", "вт", "ср", "чт", "пт", "сб")


def start_greetings(message: types.Message):
    bot.send_message(ADMIN_ID, f"{detect_user(message)} запустил бота")
    message1 = (f"<b>Добро пожаловать в бота <em>208itc</em>!</b>"
                f"\n<em>Персональный бот 208 группы ФКиСКД БГУКИ</em>\n")

    message2 = (f"\n<b>ℹ️Что бот умеет?</b>\n"
                f"\n- <em>Отправлять расписание</em>"
                f"\n- <em>Записывать и присылать кабинеты</em>"
                f"\n- <em>Отправить список преподавателей</em>"
                f"\n- <em>Отправлять погоду с утра</em>"
                f"\n- <em>и многое другое..</em>")

    photo = open(f"./bot/data/start.jpg", 'rb')

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Команды", callback_data="help")
    button2 = types.InlineKeyboardButton("Контакты", callback_data="contacts")
    markup.row(button1, button2)

    bot.send_photo(message.chat.id, photo, message1, parse_mode='html')
    time.sleep(1)
    bot.send_message(message.chat.id, message2, parse_mode="html", reply_markup=markup)


def manage_cabs(message: types.Message):
    args = message.text.split()[1:5]
    print(f"[=]{detect_user(message)} requested cabinets: {args}")
    args = [i[:4] for i in args if len(i) >= 3 and i[:3].isdigit()]

    if len(args) > 0:
        cabinets_info['cabinets'] = args
        cabinets_info['author'][message.message_id] = detect_user(message)

    if cabinets_info["cabinets"]:

        bot_reply = "<b>Кабинеты:</b>\n" + "\n".join(cabinets_info["cabinets"])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Кто прислал", callback_data="author"))
        bot.send_message(message.chat.id, bot_reply, parse_mode="html", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "<b>Кабинеты не добавлены</b>", parse_mode="html")

    bot.delete_message(message.chat.id, message.message_id)


def reply_schedule(message: types.Message):
    args = message.text.split()[1:3]
    print(f"[=]{detect_user(message)} requested schedule: {args}")
    args.extend([''] * (2 - len(args)))
    week = list(filter(lambda x: x.isdigit(), args))
    week = int(week[0]) % 20 if week else None
    day_of_week = list(filter(lambda x: x in days, args))
    day_of_week = days.index(day_of_week[0]) if day_of_week else None

    send_schedule(week, day_of_week, message.chat.id)

    bot.delete_message(message.chat.id, message.message_id)


def show_author(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id,
                              f"Прислал: {cabinets_info['author'].get(callback.message.message_id - 1, 'неизвестно')}",
                              show_alert=True)


def scroll_schedule(callback: types.CallbackQuery):
    print(
        f"[=]{detect_user(callback)} SCROLLS THROUGH THE SCHEDULE")
    week = int(callback.message.text.split()[4])
    week = week % 20 + 1 if callback.data == "next" else week % 20 - 1

    new_text = get_schedule(schedule, week)

    if callback.message.text != new_text:
        bot.edit_message_text(new_text, callback.message.chat.id, callback.message.message_id,
                              parse_mode="html", reply_markup=callback.message.reply_markup)


def weather_request(message: types.Message):
    print(
        f"[=]{detect_user(message)} REQUESTED WEATHER")
    send_weather(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)


def add_lessons_request(message: types.Message):
    if check_permissions(message.from_user.id, 3):
        args = message.text.split()[1:]

        if args:
            add_lesson(args[0], days.index(args[1]), int(args[2]) - 1, args[3])

            bot.send_message(message.chat.id,
                             f"{detect_user(message)} добавил(-а) <b><em>{args[3]}</em></b> на {args[0]} неделю(-и) в <b>{define_time[int(args[2]) - 1]}</b>",
                             parse_mode="html")
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])


def raw_lessons_request(message: types.Message):
    if check_permissions(message.from_user.id, 5):
        bot.send_message(message.chat.id, str(schedule))
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])


def random_request(message: types.Message):
    if check_permissions(message.from_user.id, 4):
        args = message.text.split()[1:]
        if args:
            bot.send_message(message.chat.id, f"Среди {', '.join(args)}, был случайно выбран {random_element(args)}")
        bot.delete_message(message.chat.id, message.message_id)
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])


def teachers_request(message: types.Message):
    args = message.text.split()[1:2]
    if args and args[0] in days:
        bot.send_message(message.chat.id, teachers_by_day(days.index(args[0])), parse_mode="html")
    bot.delete_message(message.chat.id, message.message_id)


def get_user_id(message: types.Message):
    bot.reply_to(message, message.from_user.id)


def wrong_chat_type(message: types.Message):
    bot.reply_to(message,
                 f"Используйте данную команду в {'группе' if message.chat.type == 'private' else 'личном сообщении'}.")


def delete_button(callback: types.CallbackQuery):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    bot.answer_callback_query(callback.id)


def guide_button(callback: types.CallbackQuery):
    send_guide(callback.message)
    bot.answer_callback_query(callback.id)


def contacts_button(callback: types.CallbackQuery):
    send_contacts(callback.message)
    bot.answer_callback_query(callback.id)


def send_contacts(message: types.Message):
    reply = (f"📇<b>Контакты:</b>\n"
             f"\n<u>Instagram</u>"
             f"\n- <a href='https://www.instagram.com/itinculture/'>Instagram кафедры</a>"
             f"\n- <a href='https://www.instagram.com/208itk'>Instagram группы</a>"
             f"\n\n<u>Обратная связь</u>:"
             f"\n- <a href='https://t.me/naitmag'>Создатель бота</a>")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Скрыть", callback_data="hide"))
    bot.send_message(message.chat.id, reply, parse_mode='html', disable_web_page_preview=True, reply_markup=markup)


def send_guide(message: types.Message):
    reply = (f"⚙️<b>Список команд</b>"
             f"\n\n<blockquote><b>Получить расписание</b>\n/schedule или /s</blockquote>"
             f"\n- Принимает <em>|неделя| |день|</em> в любом порядке"
             f"\n- Можно указать и только неделю"
             f"\n- Без аргументов отправит текущую неделю"
             f"\n- <b>Пример:</b> <code>/schedule 12 пн</code>"
             f"\n\n<blockquote><b>Управление кабинетами</b>\n/cabinets или /c или <u>каб</u></blockquote>"
             f"\n- Принимает <em>|кабинет| |кабинет|</em>.."
             f"\n- Максимальное количество кабинетов : 4"
             f"\n- Без аргументов отправит список кабинетов"
             f"\n- <b>Пример:</b> <code>/cabinets 508 800а</code>"
             f"\n\n<blockquote><b>Добавить занятие</b>\n/add</blockquote>"
             f"\n- Принимает <em>|период или неделя| |день недели| |номер пары| |название_пары|</em>.."
             f"\n- Опционально <em> |преподаватель| |тип пары|</em>"
             f"\n- Доступ имеют определенные пользователи"
             f"\n- <b>Пример:</b> <code>/add 2-14 ср 4 Компьютерная_графика Иванов сем.</code>"
             f"\n\n<blockquote><b>Узнать преподавателей</b>\n/teacher или /t</blockquote>"
             f"\n- Принимает <em>|день недели|</em>"
             f"\n- Покажет список предметов и преподавателей"
             f"\n- <b>Пример:</b> <code>/teacher чт</code>"
             f"\n\n<blockquote><b>Получить погоду</b>\n/weather или /w</blockquote>"
             f"\n- Отправит погоду на данный момент в городе Минск"
             f"\n- <b>Пример:</b> <code>/weather</code>"
             f"\n\n<blockquote><b>Случайный элемент</b>\n/random или /r</blockquote>"
             f"\n- Принимает <em>|элемент1| |элемент2|</em>.."
             f"\n- Случайно выберет один элемент"
             f"\n- Отлично подойдет для распределения семинаров"
             f"\n- <b>Пример:</b> <code>/random @naitmag @BotFather</code>"
             f"\n\n<blockquote><b>Ваш ID</b>\n/id</blockquote>"
             f"\n- Отправит ваш ID в Telegram"
             f"\n- Подходит для распределения прав"
             f"\n- Команда для тех. части бота"
             f"\n- <b>Пример:</b> <code>/id</code>"
             f"")

    bot.reply_to(message, reply, parse_mode="html")
