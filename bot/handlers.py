import time

import telebot.apihelper
from telebot import types

from config import cabinets_info, bot, ADMIN_ID, pages, days, define_time
from sql_requests import get_teacher, create_lesson, update_user_level
from utils import send_weather, detect_user, check_permissions, random_element, format_schedule, format_teacher


# ready to use
def start_greetings(message: types.Message):
    bot.send_message(ADMIN_ID, f"{detect_user(message)} запустил бота")

    photo = open(f"../bot/data/start.jpg", 'rb')

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Команды", callback_data="help")
    button2 = types.InlineKeyboardButton("Контакты", callback_data="contacts")
    markup.row(button1, button2)

    bot.send_photo(message.chat.id, photo, pages["home"][0], parse_mode='html')
    time.sleep(1)
    bot.send_message(message.chat.id, pages["home"][1], parse_mode="html", reply_markup=markup)


def set_permission(message: types.Message):
    if check_permissions(message, 5):

        request = message.text.split()[1:3]

        try:
            request[1] = min(int(request[1]), 5)
        except (IndexError, ValueError):
            bot.send_message(message.chat.id,
                             "<b>❌ Неверная команда!</b>\n"
                             "<i>Используйте</i> <code>/set |юзернейм| |уровень|</code>\n"
                             "Подробнее: /help", parse_mode="html")
            return

        update_user_level(request[0], request[1])
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])


# ready to use
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


# ready to use
def show_author(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id,
                              f"Прислал: {cabinets_info['author'].get(callback.message.message_id - 1, 'неизвестно')}",
                              show_alert=True)


# ready to use
def send_schedule(message: types.Message):
    args = message.text.split()[1:3]

    print(f"[=]{detect_user(message)} requested schedule: {args}")

    args.extend([''] * (2 - len(args)))
    week = list(filter(lambda x: x.isdigit(), args))
    week = int(week[0]) % 20 if week else None
    day_of_the_week = list(filter(lambda x: x in days, args))
    day_of_the_week = days.index(day_of_the_week[0]) if day_of_the_week else None

    markup = types.InlineKeyboardMarkup()
    if day_of_the_week is None:
        button1 = types.InlineKeyboardButton("◀️", callback_data="back")
        button2 = types.InlineKeyboardButton("▶️", callback_data="next")
        markup.row(button1, button2)

    bot.send_message(message.chat.id, format_schedule(week, day_of_the_week), parse_mode='html',
                     reply_markup=markup)


def add_lesson(message: types.Message):
    if check_permissions(message, 4):
        args = message.text.split()[1:]

        try:
            args[1] = days.index(args[1])
            args[2] = int(args[2])
            args[3] = args[3].capitalize().replace('_', ' ')
            args[5] = args[5].capitalize()
        except (IndexError, ValueError):
            print(f"[!]{detect_user(message)} WRONG ARGUMENTS: {args}")

            bot.send_message(message.chat.id,
                             "<b>❌ Неверная команда!</b>\n"
                             "<i>Используйте</i> <code>/add 1-10 пн 1 "
                             "Название_пары сем. Фамилия</code>\n"
                             "Подробнее: /help", parse_mode="html")
        else:
            create_lesson(*args[:6])
            bot.send_message(message.chat.id,
                             f"ℹ️ <b>{detect_user(message)}</b> добавил(-а):\n"
                             f" - <b><em>{args[4] if args[4] == '-' else ''} {args[3]}</em></b>"
                             f" в <b>{define_time[args[1]]}</b> на <b>{args[0]}</b> недели(-ю)",
                             parse_mode="html")

        bot.delete_message(message.chat.id, message.message_id)
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])


# ready to use !!need formatting!!
def send_teacher(message: types.Message):
    args = message.text.split()[1:]
    if args:
        result = (f"Занятия по запросу '{args[0]}' :\n"
                  f"{format_teacher(get_teacher(args[0]))}")
        bot.send_message(message.chat.id, result)


# old
def weather_request(message: types.Message):
    print(
        f"[=]{detect_user(message)} REQUESTED WEATHER")
    send_weather(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)


# old
def random_request(message: types.Message):
    if check_permissions(message, 4):
        args = message.text.split()[1:]
        if args:
            bot.send_message(message.chat.id, f"Среди {', '.join(args)}, был случайно выбран {random_element(args)}")
        bot.delete_message(message.chat.id, message.message_id)
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])


# old
def send_user_id(message: types.Message):
    bot.reply_to(message, message.from_user.id)


def wrong_chat_type(message: types.Message):
    bot.reply_to(message,
                 f"Используйте данную команду в {'группе' if message.chat.type == 'private' else 'личном сообщении'}.")


def home_page(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Команды", callback_data="help")
    button2 = types.InlineKeyboardButton("Контакты", callback_data="contacts")
    markup.row(button1, button2)
    bot.edit_message_text(pages["home"][1], callback.message.chat.id, callback.message.message_id, parse_mode="html",
                          reply_markup=markup)


def pages_button(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Назад", callback_data="home"))
    bot.edit_message_text(pages[callback.data], callback.message.chat.id, callback.message.message_id,
                          parse_mode="html", disable_web_page_preview=True, reply_markup=markup)


def delete_button(callback: types.CallbackQuery):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)


def send_contacts(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Скрыть", callback_data="hide"))
    bot.send_message(message.chat.id, pages["contacts"], parse_mode='html', disable_web_page_preview=True,
                     reply_markup=markup)
    bot.delete_message(message.chat.id, message.message_id)


def send_guide(message: types.Message):
    bot.reply_to(message, pages["help"], parse_mode="html")


def scroll_schedule(callback: types.CallbackQuery):
    week = int(callback.message.text.split()[4])
    week = week % 20 + 1 if callback.data == "next" else week % 20 - 1

    result = format_schedule(week)

    try:
        bot.edit_message_text(result, callback.message.chat.id, callback.message.message_id,
                              parse_mode="html", reply_markup=callback.message.reply_markup)
    except telebot.apihelper.ApiTelegramException:
        print(f"[!]{detect_user(callback)} TO MANY CALLBACK REQUESTS")
