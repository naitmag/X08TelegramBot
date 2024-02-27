import sqlite3

from telebot import types

import config
from config import bot
from handlers.user_states import LessonsRequestState
from sql_requests import delete_lesson, create_lesson
from utils import format_schedule, get_current_week, log_info


def manage_lessons(message: types.Message):
    bot.set_state(message.from_user.id, LessonsRequestState.get_week, message.chat.id)

    log_info(message, "started adding new lesson")

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Текущая", callback_data="current_week"),
        types.InlineKeyboardButton("Следующая", callback_data="next_week"),
        types.InlineKeyboardButton("Отмена", callback_data="cancel_request"),
        row_width=1
    )

    with (bot.retrieve_data(message.from_user.id, message.chat.id) as data):
        data['action'] = message.text.split()[0][1:]
        data['progress'] = f"<b>{'➕ Добавить занятие' if data['action'] == 'add' else '➖ Удалить занятие'}</b>\n"

        data['message_id'] = bot.send_message(message.chat.id, data['progress'] + "➡️ Введите неделю или интервал:",
                                              parse_mode='html',
                                              reply_markup=markup).message_id


def input_week(querry: types.Message | types.CallbackQuery):
    if isinstance(querry, types.CallbackQuery):
        week = str(get_current_week() + (1 if querry.data == "next_week" else 0))
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

            types.InlineKeyboardButton("Понедельник", callback_data='0'),
            types.InlineKeyboardButton("Вторник", callback_data='1'),
            types.InlineKeyboardButton("Среда", callback_data='2'),
            types.InlineKeyboardButton("Четверг", callback_data='3'),
            types.InlineKeyboardButton("Пятница", callback_data='4'),
            types.InlineKeyboardButton("Суббота", callback_data='5'),
            row_width=2
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

            types.InlineKeyboardButton("8:00", callback_data='0'),
            types.InlineKeyboardButton("9:35", callback_data='1'),
            types.InlineKeyboardButton("11:10", callback_data='2'),
            types.InlineKeyboardButton("13:00", callback_data='3'),
            types.InlineKeyboardButton("14:35", callback_data='4'),
            types.InlineKeyboardButton("16.10", callback_data='5'),
            types.InlineKeyboardButton("Отмена", callback_data="cancel_request"),
            row_width=3
        )

        bot.edit_message_text(data['progress'] + "➡️ Выберите время:", callback.message.chat.id, data['message_id'],
                              parse_mode='html', reply_markup=markup)

        bot.set_state(callback.from_user.id, LessonsRequestState.get_lesson_number, callback.message.chat.id)


def input_lesson_number(callback: types.CallbackQuery):
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data['lesson_number'] = int(callback.data)
        data['progress'] += f"🕘 <b>{config.define_time[data['lesson_number']]}</b>\n"

    markup = types.InlineKeyboardMarkup()

    markup.add(

        types.InlineKeyboardButton("л.", callback_data='0'),
        types.InlineKeyboardButton("сем.", callback_data='1'),
        types.InlineKeyboardButton("пр.", callback_data='2'),
        types.InlineKeyboardButton("лаб.", callback_data='3'),
        types.InlineKeyboardButton("спорт.", callback_data='4'),
        types.InlineKeyboardButton("кардио", callback_data='5'),
        types.InlineKeyboardButton("сил.", callback_data='6'),
        types.InlineKeyboardButton("доп.", callback_data='7'),
        types.InlineKeyboardButton("Отмена", callback_data="cancel_request"),
        row_width=2
    )

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
    markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))

    if data['action'] == 'add':
        next_step = "➡️ Введите преподавателя:"
        bot.set_state(message.from_user.id, LessonsRequestState.get_teacher, message.chat.id)
    else:
        next_step = "➡️ Данные введены верно?"
        bot.set_state(message.from_user.id, LessonsRequestState.confirm_input, message.chat.id)
        markup.add(types.InlineKeyboardButton("Подтвердить", callback_data="confirm_lesson"))

    bot.edit_message_text(data['progress'] + next_step, message.chat.id, data['message_id'],
                          parse_mode='html', reply_markup=markup)

    bot.delete_message(message.chat.id, message.message_id)


def input_lesson_teacher(message: types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['teacher'] = message.text
        data['progress'] += f"👨‍🎓 <b>{data['teacher']}</b>\n"

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton("Подтвердить", callback_data="confirm_lesson"),
            types.InlineKeyboardButton("Отмена", callback_data="cancel_request"),
            row_width=1
        )

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
        data['progress'] = '1'
        log_info(callback, f"changed lessons: {data}")
    bot.delete_state(callback.from_user.id, callback.message.chat.id)
