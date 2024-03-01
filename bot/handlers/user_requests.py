import os
import random
import time

import telebot.apihelper
from telebot import types

from config import cabinets_info, bot, GROUP_ID
from handlers.user_states import TeachersRequestState
from sql_requests import get_teacher
from utils import detect_user, random_element, format_teacher, get_weather, log_info


def manage_cabs(message: types.Message):
    log_info(message)

    args = message.text.split()[1:5]
    cabs = [i for i in args if len(i) > 2 and i[:3].isdigit() and not i[3:].isdigit()]
    if cabs == args:
        if len(args) > 0:
            cabinets_info['cabinets'] = args
            cabinets_info['author'] = detect_user(message)
            bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("❤️‍🔥")])

        if cabinets_info["cabinets"]:

            bot_reply = ("<b>Кабинеты:</b>\n - " +
                         "\n - ".join(cabinets_info["cabinets"]).replace('(', ' (').replace('_', ' '))
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Кто прислал", callback_data="cabs_author"))
            bot.send_message(message.chat.id, bot_reply, parse_mode="html", reply_markup=markup)

        else:
            bot.send_message(message.chat.id, "<b>Кабинеты не добавлены</b>", parse_mode="html")


def show_author(callback: types.CallbackQuery):
    log_info(callback)
    bot.answer_callback_query(callback.id,
                              f"Прислал: {cabinets_info['author']}",
                              show_alert=True)


def find_teachers(message: types.Message):
    log_info(message)
    bot.set_state(message.from_user.id, TeachersRequestState.request, message.chat.id)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_request"))
    sended_message = bot.send_message(message.chat.id,
                                      "🔍 <b>Введите <em>название предмета</em> или <em>фамилию</em>.</b>",
                                      parse_mode='html', reply_markup=markup)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['message_id'] = sended_message.message_id


def send_teacher(message: types.Message):
    log_info(message)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        result = (f"🔍 Занятия по запросу '<u>{message.text}</u>' :\n"
                  f"{format_teacher(get_teacher(message.text))}")

        bot.edit_message_text(result, message.chat.id, data['message_id'],
                              parse_mode='html')
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)


def cancel_request(callback: types.CallbackQuery):
    log_info(callback)
    try:
        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            if len(data) > 0:
                bot.edit_message_text("🔍 <b>Запрос был отменен.</b>", callback.message.chat.id,
                                      callback.message.message_id,
                                      parse_mode='html')

    except telebot.apihelper:
        bot.answer_callback_query(callback.id, "Вы не отправляли запрос!", show_alert=True)
        return
    bot.delete_state(callback.from_user.id, callback.message.chat.id)


def send_weather(message: types.Message = None):
    if message:
        log_info(message)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Обновить", callback_data="update_weather"))

    picture_number = random.randint(0, 2)
    picture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'img', 'weather',
                                f'{picture_number}.jpg')

    with open(picture_path, 'rb') as photo:
        bot.send_photo(GROUP_ID if message is None else message.chat.id, photo, get_weather(), parse_mode="html",
                       reply_markup=markup)


def update_weather(callback: types.CallbackQuery):
    log_info(callback)

    result = get_weather()
    try:
        bot.edit_message_caption(result, callback.message.chat.id, callback.message.message_id, parse_mode='html',
                                 reply_markup=callback.message.reply_markup)
    except telebot.apihelper.ApiTelegramException:
        pass
    bot.answer_callback_query(callback.id, "Погода обновлена!", show_alert=True)


def random_request(message: types.Message):
    log_info(message)

    args = message.text.split()[1:]
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
