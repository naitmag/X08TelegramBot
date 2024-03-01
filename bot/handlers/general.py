import random

from telebot import types
from bot.config import bot, events
from bot.utils import log_info


def send_id(message: types.Message):
    log_info(message)
    bot.reply_to(message,
                 f"ID: {message.from_user.id}\n{f'CHAT: {message.chat.id}' if message.chat.type != 'private' else ''}")


def wrong_chat_type(message: types.Message):
    log_info(message)
    markup = types.InlineKeyboardMarkup()
    if message.chat.type == 'supergroup':
        markup.add(types.InlineKeyboardButton("Перейти", url="https://t.me/itcX08bot"))
    bot.send_message(message.chat.id,
                     f"Используйте данную команду в "
                     f"{'группе' if message.chat.type == 'private' else 'личном сообщении'}.",
                     reply_markup=markup, disable_web_page_preview=True)


def check_text_event(message: types.Message):
    log_info(message)
    current_chance = random.randint(0, 100)
    check_list = list(events['text'].items())
    for item in check_list:
        if item[0] in message.text.lower():
            if current_chance <= item[1][0]:
                bot.reply_to(message, item[1][1])
                return


def check_photo_event(message: types.Message):
    log_info(message, f'Photo')
    if random.randint(0, 100) <= events['photo'][0]:
        bot.reply_to(message, events['photo'][1][random.randint(0, len(events['photo'][1]) - 1)])
