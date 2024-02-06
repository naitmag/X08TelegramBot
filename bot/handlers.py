import time

import telebot.apihelper
from telebot import types

from config import cabinets_info, bot, ADMIN_ID, pages, days, define_time, GROUP_ID
from sql_requests import get_teacher, create_lesson, update_user_level, delete_lesson
from utils import send_weather, detect_user, check_permissions, random_element, format_schedule, format_teacher


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


# ready
def set_permission(message: types.Message):
    if check_permissions(message, 5):

        request = message.text.split()[1:3]

        try:
            request[1] = max(min(int(request[1]), 5), -1)

            request[0] = request[0].replace('@', '')

        except (IndexError, ValueError):
            bot.send_message(message.chat.id,
                             "<b>❌ Неверная команда!</b>\n"
                             "<i>Используйте</i> <code>/set |имя пользователя| |уровень|</code>\n"
                             "Подробнее: /help", parse_mode="html")
            return
        bot.send_message(message.chat.id,
                         f"<b>✅ Уровень пользователя <i>{'' if request[0].isdigit() else '@'}{request[0]}"
                         f"</i> теперь {request[1]}</b>",
                         parse_mode='html')

        update_user_level(request[0], request[1])


# ready
def manage_cabs(message: types.Message):
    args = message.text.split()[1:5]
    print(f"[=]{detect_user(message)} requested cabinets: {args}")
    args = [i[:4] for i in args if len(i) >= 3 and i[:3].isdigit() and not i[3:].isdigit()]

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

    # bot.delete_message(message.chat.id, message.message_id)


# ready
def show_author(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id,
                              f"Прислал: {cabinets_info['author'].get(callback.message.message_id - 1, 'неизвестно')}",
                              show_alert=True)


# ready to use
def send_schedule(message: types.Message = None):
    if not message:
        bot.send_message(GROUP_ID, format_schedule(), parse_mode='html')
        return

    args = message.text.split()[1:3]
    print(f"[=]{detect_user(message)} requested schedule: {args}")

    args.extend([''] * (2 - len(args)))
    week = list(filter(lambda x: x.isdigit(), args))
    week = int(week[0]) % 21 if week else None
    day_of_the_week = list(filter(lambda x: x in days, args))
    day_of_the_week = days.get(day_of_the_week[0]) if day_of_the_week else None

    markup = types.InlineKeyboardMarkup()
    if day_of_the_week is None:
        button1 = types.InlineKeyboardButton("◀️", callback_data="back")
        button2 = types.InlineKeyboardButton("▶️", callback_data="next")
        markup.row(button1, button2)

    bot.send_message(message.chat.id, format_schedule(week, day_of_the_week), parse_mode='html',
                     reply_markup=markup)
    bot.delete_message(message.chat.id, message.message_id)


def add_lesson(message: types.Message):
    if check_permissions(message, 4):
        args = message.text.split()[1:]
        try:

            interval = args[0].split('-')
            start = int(interval[0])
            end = int(interval[0] if len(interval) <= 1 else interval[1])

            if 0 <= start <= 20 and start <= end <= 20:

                args[1] = days.get(args[1])
                args[2] = int(args[2]) - 1
                args[3] = args[3].capitalize().replace('_', ' ')
                if len(args) > 5:
                    args[5] = args[5].capitalize()
            else:
                bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])
                return

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
                             f" - <b><em> {args[4] if len(args) > 4 else 'доп.'} {args[3]}</em></b>"
                             f" в <b>{days.get(args[1])} {define_time[args[2]]}</b> на <b>{args[0]}</b> неделю(-и)",
                             parse_mode="html")

        ...  # wrong weeks

        # bot.delete_message(message.chat.id, message.message_id)


def remove_lesson(message: types.Message):
    if check_permissions(message, 4):
        args = message.text.split()[1:]
        try:
            args[0] = days.get(args[0])
            args[1] = int(args[1]) - 1
            args[2] = args[2].replace('_', ' ')

        except (IndexError, ValueError):
            print(f"[!]{detect_user(message)} WRONG ARGUMENTS: {args}")

            bot.send_message(message.chat.id,
                             "<b>❌ Неверная команда!</b>\n"
                             "<i>Используйте</i> <code>/remove пн 1 Название_пары </code>"
                             "Подробнее: /help", parse_mode="html")
        else:
            data = delete_lesson(*args[:3])
            print(data)
            if len(data) == 1:
                bot.send_message(message.chat.id,
                                 f"ℹ️ <b>{detect_user(message)}</b> удалил(-а):\n"
                                 f" - <b><em>{data[0][2]} {data[0][3]}</em></b>"
                                 f" в <b>{define_time[data[0][1]]}</b> на "
                                 f"<b>{data[0][4]}{'' if data[0][4] == data[0][5] else data[0][5]}</b> неделe(-ях)",
                                 parse_mode="html")
            else:
                bot.send_message(message.chat.id,
                                 f"<b>❌ {"Слишком много результатов!" if len(data) > 1 else "Нет результатов"}</b>\n",
                                 parse_mode='html')

        bot.delete_message(message.chat.id, message.message_id)


def send_teacher(message: types.Message):
    args = message.text.lower().split()[1:]

    if args and len(args[0]) >= 3:
        result = (f"🔍 Занятия по запросу '<u>{args[0]}</u>' :\n"
                  f"{format_teacher(get_teacher(args[0]))}")
        bot.send_message(message.chat.id, result, parse_mode="html")
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("👀")])


def weather_request(message: types.Message):
    print(f"[=]{detect_user(message)} REQUESTED WEATHER")
    send_weather(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)


# old
def random_request(message: types.Message):
    if check_permissions(message, 4):
        args = message.text.split()[1:]
        if args and len(args) >= 2:
            bot.send_message(message.chat.id, f"Среди {', '.join(args)}, был случайно выбран {random_element(args)}")
        bot.delete_message(message.chat.id, message.message_id)


# old
def send_id(message: types.Message):
    bot.reply_to(message,
                 f"ID: {message.from_user.id}\n{f'CHAT: {message.chat.id}' if message.chat.type != 'private' else ''}")


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
    week = week - (-1 if callback.data == 'next' else 1)
    week = (week - 1 if week == 0 else week) % 21

    result = format_schedule(week)

    if result != callback.message.text:
        try:
            bot.edit_message_text(result, callback.message.chat.id, callback.message.message_id,
                                  parse_mode="html", reply_markup=callback.message.reply_markup)
        except telebot.apihelper.ApiTelegramException:
            print(f"[!]{detect_user(callback)} TO MANY CALLBACK REQUESTS")
