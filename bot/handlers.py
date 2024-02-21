import sqlite3
import time
from datetime import datetime
from pathlib import Path
import random

import telebot.apihelper
from telebot import types
from telebot.handler_backends import StatesGroup, State

import config
from config import cabinets_info, bot, ADMIN_ID, pages, days, define_time, GROUP_ID, roles, events
from sql_requests import get_teacher, update_user_level, delete_lesson, get_user, create_lesson
from utils import detect_user, random_element, format_schedule, format_teacher, detect_chat, get_weather, \
    get_current_week


class TeachersRequestState(StatesGroup):
    request = State()


class LessonsRequestState(StatesGroup):
    get_week = State()
    get_day_of_the_week = State()
    get_lesson_number = State()
    get_lesson_name = State()
    get_lesson_type = State()
    get_teacher = State()
    confirm_input = State()


def start_greetings(message: types.Message):
    print(f"[=]{detect_user(message)} started the bot")
    photo = open(f"{Path(__file__).parent.resolve()}/data/img/pages/start.jpg", 'rb')

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Команды", callback_data="help")
    button2 = types.InlineKeyboardButton("Роли", callback_data="roles")
    markup.row(button1, button2)
    markup.add(types.InlineKeyboardButton("Контакты", callback_data="contacts"))

    bot.send_photo(message.chat.id, photo, pages["home"][0], parse_mode='html')
    time.sleep(1)
    bot.send_message(message.chat.id, pages["home"][1], parse_mode="html", reply_markup=markup)
    time.sleep(1)
    bot.send_message(ADMIN_ID, f"{detect_user(message)} запустил бота")


def switch_admin_mode(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        config.admin_mode = not config.admin_mode
        bot.send_message(message.chat.id, f"🔐 Режим админа теперь: {config.admin_mode} /am")
        bot.delete_message(message.chat.id, message.message_id)
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("😨")])


def set_permission(message: types.Message):
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
                     f"☑️ <b><i>{'' if request[0].isdigit() else '@'}{request[0]} </i></b>"
                     f"теперь <b>{roles[request[1]]}</b>",
                     parse_mode='html')
    update_user_level(request[0], request[1])
    print(f"[A]({detect_chat(message)}){detect_user(message)} set {request[0]} level to {request[1]}")
    bot.delete_message(message.chat.id, message.message_id)


def show_permission(message: types.Message):
    request = message.text.split()[1:2]
    request[0] = request[0].replace('@', '')
    data = get_user(request[0])
    if data:
        bot.send_message(message.chat.id,
                         f"🧙🏼 Роль пользователя <i>"
                         f"<b>{'' if request[0].isdigit() else '@'}{request[0]}</b></i>: <b>{roles[data[5]]}</b>",
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id, f"🧙🏼 <b>Пользователь не найден</b>", parse_mode='html')
    bot.delete_message(message.chat.id, message.message_id)


def manage_cabs(message: types.Message):
    args = message.text.split()[1:5]
    print(f"[?]({detect_chat(message)}){detect_user(message)} requested cabinets: {args}")
    cabs = [i for i in args if len(i) > 2 and i[:3].isdigit() and not i[3:].isdigit()]
    if cabs == args:
        if len(args) > 0:
            cabinets_info['cabinets'] = args
            cabinets_info['author'] = detect_user(message)

        if cabinets_info["cabinets"]:

            bot_reply = ("<b>Кабинеты:</b>\n - " +
                         "\n - ".join(cabinets_info["cabinets"]).replace('(', ' (').replace('_', ' '))
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Кто прислал", callback_data="author"))
            bot.send_message(message.chat.id, bot_reply, parse_mode="html", reply_markup=markup)

        else:
            bot.send_message(message.chat.id, "<b>Кабинеты не добавлены</b>", parse_mode="html")


def show_author(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id,
                              f"Прислал: {cabinets_info['author']}",
                              show_alert=True)


def send_schedule(message: types.Message = None):
    if not message:
        bot.send_message(GROUP_ID, format_schedule(), parse_mode='html')
        return

    args = message.text.split()[1:3]
    print(f"[?]({detect_chat(message)}){detect_user(message)} requested schedule: {args}")

    args.extend([''] * (2 - len(args)))
    week = list(filter(lambda x: x.isdigit(), args))
    week = int(week[0]) % 21 if week else None
    day_of_the_week = list(filter(lambda x: x in days, args))
    day_of_the_week = days.get(day_of_the_week[0]) if day_of_the_week else None

    markup = types.InlineKeyboardMarkup()

    if day_of_the_week is None:

        markup.row(types.InlineKeyboardButton("◀️", callback_data="back"),
                   types.InlineKeyboardButton("▶️", callback_data="next"))

        if week is not None and week != get_current_week():
            markup.add(types.InlineKeyboardButton("⏏️", callback_data="scroll_current_week"))

    bot.send_message(message.chat.id, format_schedule(week, day_of_the_week), parse_mode='html',
                     reply_markup=markup)


def manage_lessons(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Текущая", callback_data="current_week"))
    markup.add(types.InlineKeyboardButton("Следующая", callback_data="next_week"))
    markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))
    bot.set_state(message.from_user.id, LessonsRequestState.get_week, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['action'] = message.text.split()[0][1:]
        data['progress'] = f"<b>{'➕ Добавить занятие' if data['action'] == 'add' else '➖ Удалить занятие'}</b>\n"
        sended_message = bot.send_message(message.chat.id, data['progress'] + "➡️ Введите неделю:", parse_mode='html',
                                          reply_markup=markup)
        data['message_id'] = sended_message.message_id


def input_week(querry: types.Message | types.CallbackQuery):
    if type(querry) is types.CallbackQuery:
        week = str(
            max((datetime.now() - config.START_LESSONS).days // 7 + 1 + (1 if querry.data == "next_week" else 0), 1))
        chat_id = querry.message.chat.id
    else:
        week = querry.text
        try:
            list(map(lambda x: int(x), week.split('-')))
        except ValueError:
            return
        chat_id = querry.chat.id
        bot.delete_message(chat_id, querry.message_id)

    with bot.retrieve_data(querry.from_user.id, chat_id) as data:
        data['week'] = week
        data['progress'] += f"📆 <b>{data['week']}</b> неделя(-и)\n"

        markup = types.InlineKeyboardMarkup()
        markup.add(
            *(
                types.InlineKeyboardButton("Понедельник", callback_data='0'),
                types.InlineKeyboardButton("Вторник", callback_data='1')
            )
        )
        markup.add(
            *(
                types.InlineKeyboardButton("Среда", callback_data='2'),
                types.InlineKeyboardButton("Четверг", callback_data='3'),
            )
        )
        markup.add(
            *(
                types.InlineKeyboardButton("Пятница", callback_data='4'),
                types.InlineKeyboardButton("Суббота", callback_data='5')
            )
        )

        markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))

        bot.edit_message_text(data['progress'] + "➡️ Выберите день недели:", chat_id, data['message_id'],
                              parse_mode='html', reply_markup=markup)

        bot.set_state(querry.from_user.id, LessonsRequestState.get_day_of_the_week, chat_id)


def input_day_of_the_week(callback: types.CallbackQuery):
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data['day_of_the_week'] = int(callback.data)
        if data['action'] == 'add':
            data['progress'] += f"☀️ {config.define_week[data['day_of_the_week']][2:]}\n"
        else:
            data['progress'] += format_schedule(int(data['week']), data['day_of_the_week'])

        markup = types.InlineKeyboardMarkup()

        markup.add(
            *(
                types.InlineKeyboardButton("8:00", callback_data='0'),
                types.InlineKeyboardButton("9:35", callback_data='1'),
                types.InlineKeyboardButton("11:10", callback_data='2'),
                types.InlineKeyboardButton("13:00", callback_data='3'),
                types.InlineKeyboardButton("14:35", callback_data='4'),
                types.InlineKeyboardButton("16.10", callback_data='5'),

            )
        )
        markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))

        bot.edit_message_text(data['progress'] + "➡️ Выберите время:", callback.message.chat.id, data['message_id'],
                              parse_mode='html', reply_markup=markup)

        bot.set_state(callback.from_user.id, LessonsRequestState.get_lesson_number, callback.message.chat.id)


def input_lesson_number(callback: types.CallbackQuery):
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data['lesson_number'] = int(callback.data)
        data['progress'] += f"🕘 <b>{config.define_time[data['lesson_number']]}</b>\n"

    markup = types.InlineKeyboardMarkup()

    markup.add(
        *(
            types.InlineKeyboardButton("л.", callback_data='0'),
            types.InlineKeyboardButton("сем.", callback_data='1'),
            types.InlineKeyboardButton("пр.", callback_data='2'),
            types.InlineKeyboardButton("лаб.", callback_data='3'),
            types.InlineKeyboardButton("спорт.", callback_data='4'),
            types.InlineKeyboardButton("кардио", callback_data='5'),
            types.InlineKeyboardButton("сил.", callback_data='6'),
            types.InlineKeyboardButton("доп.", callback_data='7'),
            types.InlineKeyboardButton("Отмена", callback_data="cancel_request")
        )
    )
    markup.add()

    bot.edit_message_text(data['progress'] + "➡️ Выберите тип занятия:", callback.message.chat.id, data['message_id'],
                          parse_mode='html', reply_markup=markup)

    bot.set_state(callback.from_user.id, LessonsRequestState.get_lesson_type, callback.message.chat.id)


def input_lesson_type(callback: types.CallbackQuery):
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data['lesson_type'] = config.define_lesson_type[int(callback.data)]
        data['progress'] += f"🔘 <b>{data['lesson_type']}</b>\n"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))

    bot.edit_message_text(data['progress'] + "➡️ Введите название занятия:", callback.message.chat.id,
                          data['message_id'],
                          parse_mode='html', reply_markup=markup)

    bot.set_state(callback.from_user.id, LessonsRequestState.get_lesson_name, callback.message.chat.id)


def input_lesson_name(message: types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['lesson_name'] = message.text
        data['progress'] += f"📕 <b><em>{data['lesson_name']}</em></b>\n"

    markup = types.InlineKeyboardMarkup()

    if data['action'] == 'add':
        next_step = "➡️ Введите преподавателя:"
        bot.set_state(message.from_user.id, LessonsRequestState.get_teacher, message.chat.id)
    else:
        next_step = "➡️ Данные введены верно?"
        bot.set_state(message.from_user.id, LessonsRequestState.confirm_input, message.chat.id)
        markup.add(types.InlineKeyboardButton("Подтвердить", callback_data="confirm_lesson"))

    markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))
    bot.edit_message_text(data['progress'] + next_step, message.chat.id, data['message_id'],
                          parse_mode='html', reply_markup=markup)

    bot.delete_message(message.chat.id, message.message_id)


def input_lesson_teacher(message: types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['teacher'] = message.text
        data['progress'] += f"👨‍🎓 <b>{data['teacher']}</b>\n"

        markup = types.InlineKeyboardMarkup()

        markup.add(types.InlineKeyboardButton("Подтвердить", callback_data="confirm_lesson"))
        markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))

        bot.edit_message_text(data['progress'] + "➡️ Данные введены верно?", message.chat.id, data['message_id'],
                              parse_mode='html', reply_markup=markup)

        bot.set_state(message.from_user.id, LessonsRequestState.confirm_input, message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)


def confirm_lesson(callback: types.CallbackQuery):
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        if data['action'] == 'add':
            try:
                create_lesson(data['week'], data['day_of_the_week'], data['lesson_number'], data['lesson_name'],
                              data['lesson_type'], data['teacher'])
            except sqlite3.OperationalError:
                bot.answer_callback_query(callback.from_user.id, "Неверные аргументы!", show_alert=True)

            bot.edit_message_text(f"ℹ️ <b>Новое занятие в расписании:</b>\n"
                                  f"📆 Неделя(-и) <b>{data['week']}</b>\n"
                                  f"<b>{config.define_week[data['day_of_the_week']]}</b>\n"
                                  f"<b>- {config.define_time[data['lesson_number']]}</b> "
                                  f"<em>{data['lesson_type']} {data['lesson_name']}</em>",
                                  callback.message.chat.id, data['message_id'],
                                  parse_mode='html')
        else:
            result = delete_lesson(data['week'], data['day_of_the_week'], data['lesson_number'], data['lesson_type'],
                                   data['lesson_name'])
            if result:
                if len(result) == 1:
                    bot.edit_message_text(f"ℹ️ <b>Занятие отменено:</b>\n"
                                          f"📆 Неделя(-и) <b>{data['week']}</b>\n"
                                          f"<b>{config.define_week[data['day_of_the_week']]}</b>\n"
                                          f"<b>- {config.define_time[data['lesson_number']]}</b> "
                                          f"<em>{data['lesson_type']} {result[0][3]}</em>",
                                          callback.message.chat.id, data['message_id'],
                                          parse_mode='html')
                elif len(result) > 1:
                    bot.edit_message_text(f"❌ <b>Слишком много результатов</b>\n"
                                          f" - Повторите попытку\n",
                                          callback.message.chat.id, data['message_id'],
                                          parse_mode='html')
            else:
                bot.edit_message_text(f"❌ <b>Не найдено занятий по запросу</b>\n"
                                      f" - Повторите попытку\n",
                                      callback.message.chat.id, data['message_id'],
                                      parse_mode='html')


def remove_lesson(message: types.Message):
    args = message.text.split()[1:]
    print(f"[R]({detect_chat(message)}){detect_user(message)} removes lessons {args}")
    try:
        args[0] = days.get(args[0])
        args[1] = int(args[1]) - 1
        args[2] = args[2].replace('_', ' ')

    except (IndexError, ValueError):
        print(f"[!]({detect_chat(message)}){detect_user(message)} WRONG ARGUMENTS: {args}")

        bot.send_message(message.chat.id,
                         "<b>❌ Неверная команда!</b>\n"
                         "<i>Используйте</i> <code>/remove пн 1 Название_пары </code>"
                         "Подробнее: /help", parse_mode="html")
    else:
        data = delete_lesson(*args[:3])
        if len(data) == 1:
            bot.send_message(message.chat.id,
                             f"ℹ️ <b>{detect_user(message)}</b> удалил(-а):\n"
                             f" - <b><em>{data[0][2]} {data[0][3]}</em></b>"
                             f" в <b>{define_time[data[0][1]]}</b> на "
                             f"<b>{data[0][4]}{'' if data[0][4] == data[0][5] else data[0][5]}</b> неделe(-ях)",
                             parse_mode="html")
        else:
            bot.send_message(message.chat.id,
                             f"<b>❌ {'Слишком много результатов!' if len(data) > 1 else 'Нет результатов'}</b>\n",
                             parse_mode='html')


def find_teachers(message: types.Message):
    bot.set_state(message.from_user.id, TeachersRequestState.request, message.chat.id)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))
    sended_message = bot.send_message(message.chat.id,
                                      "🔍 <b>Введите <em>название предмета</em> или <em>фамилию</em>.</b>",
                                      parse_mode='html', reply_markup=markup)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['message_id'] = sended_message.message_id


def send_teacher(message: types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        result = (f"🔍 Занятия по запросу '<u>{message.text}</u>' :\n"
                  f"{format_teacher(get_teacher(message.text))}")

        bot.edit_message_text(result, message.chat.id, data['message_id'],
                              parse_mode='html')
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)


def cancel_request(callback: types.CallbackQuery):
    try:
        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            if len(data) > 0:
                bot.edit_message_text("🔍 <b>Запрос был отменен.</b>", callback.message.chat.id,
                                      callback.message.message_id,
                                      parse_mode='html')


    except:
        bot.answer_callback_query(callback.id, "Вы не отправляли запрос!", show_alert=True)
        return
    bot.delete_state(callback.from_user.id, callback.message.chat.id)


def send_weather(message: types.Message = None):
    if message:
        print(f"[?]({detect_chat(message)}){detect_user(message)} requested weather")
    picture_number = random.randint(0, 2)
    path = f"{Path(__file__).parent.resolve()}/data/img/weather/{picture_number}.jpg"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Обновить", callback_data="update_weather"))
    file = open(path, 'rb')
    bot.send_photo(GROUP_ID if message is None else message.chat.id, file, get_weather(), parse_mode="html",
                   reply_markup=markup)
    file.close()


def update_weather(callback: types.CallbackQuery):
    result = get_weather()
    try:
        bot.edit_message_caption(result, callback.message.chat.id, callback.message.message_id, parse_mode='html',
                                 reply_markup=callback.message.reply_markup)
    except telebot.apihelper.ApiTelegramException:
        pass
    bot.answer_callback_query(callback.id, "Погода обновлена!", show_alert=True)


def random_request(message: types.Message):
    args = message.text.split()[1:]
    print(f"[?]({detect_chat(message)}){detect_user(message)} randomize {args}")
    if args and len(args) >= 2:
        bot.send_dice(message.chat.id)
        time.sleep(4)
        bot.send_message(message.chat.id,
                         f"🎲 Среди <i>{', '.join(args).replace('_', ' ')}</i>"
                         f"\nбыл случайно выбран:"
                         f"\n<b> - <u>{random_element(args).replace('_', ' ')}</u></b>",
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id, "<b>🎲 Введите список элементов</b>\n"
                                          "<code>/random элемент1 элемент2</code>", parse_mode='html')


def send_id(message: types.Message):
    bot.reply_to(message,
                 f"ID: {message.from_user.id}\n{f'CHAT: {message.chat.id}' if message.chat.type != 'private' else ''}")


def wrong_chat_type(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    if message.chat.type == 'supergroup':
        markup.add(types.InlineKeyboardButton("Перейти", url="https://t.me/testbot208_bot"))
    bot.send_message(message.chat.id,
                     f"Используйте данную команду в "
                     f"{'группе' if message.chat.type == 'private' else 'личном сообщении'}.",
                     reply_markup=markup, disable_web_page_preview=True)


def check_text_event(message: types.Message):
    current_chance = random.randint(0, 100)
    check_list = list(events['text'].items())
    for item in check_list:
        if item[0] in message.text.lower():
            if current_chance <= item[1][0]:
                bot.reply_to(message, item[1][1])
                return


def check_photo_event(message: types.Message):
    if random.randint(0, 100) <= events['photo'][0]:
        bot.reply_to(message, events['photo'][1][random.randint(0, len(events['photo'][1]) - 1)])


def home_page(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Команды", callback_data="help")
    button2 = types.InlineKeyboardButton("Роли", callback_data="roles")
    markup.row(button1, button2)
    markup.add(types.InlineKeyboardButton("Контакты", callback_data="contacts"))
    bot.edit_message_text(pages["home"][1], callback.message.chat.id, callback.message.message_id, parse_mode="html",
                          reply_markup=markup)


def pages_button(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Назад", callback_data="home"))
    bot.edit_message_text(pages[callback.data], callback.message.chat.id, callback.message.message_id,
                          parse_mode="html", disable_web_page_preview=True, reply_markup=markup)


def send_roles(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Скрыть", callback_data='hide'))
    bot.send_message(message.chat.id, pages['roles'], parse_mode='html', reply_markup=markup)


def send_guide(message: types.Message):
    if message.chat.type == 'supergroup':
        bot.reply_to(message, pages["help"], parse_mode="html")
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Скрыть", callback_data='hide'))
    bot.send_message(message.chat.id, pages['help'], parse_mode='html', reply_markup=markup)
    bot.delete_message(message.chat.id, message.message_id)


def admin_guide(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Скрыть", callback_data="hide"))
    bot.send_message(message.chat.id, pages["admin"], parse_mode="html", reply_markup=markup)
    bot.delete_message(message.chat.id, message.message_id)


def scroll_schedule(callback: types.CallbackQuery):
    week = int(callback.message.text.split()[4])
    week = week - (-1 if callback.data == 'next' else 1)
    week = (week - 1 if week == 0 else week) % 21
    print(f"[>]({detect_chat(callback.message)}){detect_user(callback)} scrolls schedule")
    result = format_schedule(week)

    if result != callback.message.text:
        try:
            markup = callback.message.reply_markup
            if week != get_current_week() and len(callback.message.reply_markup.keyboard) <= 1:
                markup.add(types.InlineKeyboardButton("⏏️", callback_data="scroll_current_week"))
            bot.edit_message_text(result, callback.message.chat.id, callback.message.message_id,
                                  parse_mode="html",
                                  reply_markup=markup)
        except telebot.apihelper.ApiTelegramException:

            print(f"[!]{detect_chat(callback.message)}{detect_user(callback)} TO MANY CALLBACK REQUESTS")


def scroll_current_week(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("◀️", callback_data="back"),
               types.InlineKeyboardButton("▶️", callback_data="next"))

    bot.edit_message_text(format_schedule(get_current_week()), callback.message.chat.id, callback.message.message_id,
                          parse_mode='html', reply_markup=markup)


def delete_button(callback: types.CallbackQuery):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
