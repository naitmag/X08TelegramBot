import os
import time

from telebot import types

from config import bot, ADMIN_ID
from utils import detect_user, log_info


def read_page(pagename: str, ignore_lines: int = 1):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'text', pagename + '.html')

    with open(path, 'r', encoding='utf-8') as file:
        page_content = file.readlines()[ignore_lines:]
    return ''.join(page_content)


def start_greetings(message: types.Message):
    log_info(message)

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Команды", callback_data="help")
    button2 = types.InlineKeyboardButton("Роли", callback_data="roles")
    markup.row(button1, button2)
    markup.add(types.InlineKeyboardButton("Контакты", callback_data="contacts"))

    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'img', 'pages',
                              'start.jpg')
    with open(image_path, 'rb') as image:
        bot.send_photo(message.chat.id, image, read_page('home1'), parse_mode='html')

    time.sleep(1)
    bot.send_message(message.chat.id, read_page('home2'), parse_mode="html", reply_markup=markup)
    time.sleep(1)
    bot.send_message(ADMIN_ID, f"{detect_user(message)} запустил бота")


def home_page(callback: types.CallbackQuery):
    log_info(callback)

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Команды", callback_data="help")
    button2 = types.InlineKeyboardButton("Роли", callback_data="roles")
    markup.row(button1, button2)
    markup.add(types.InlineKeyboardButton("Контакты", callback_data="contacts"))
    bot.edit_message_text(read_page('home2'), callback.message.chat.id, callback.message.message_id, parse_mode="html",
                          reply_markup=markup)


def pages_button(callback: types.CallbackQuery):
    log_info(callback)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Назад", callback_data="home2"))
    bot.edit_message_text(read_page(callback.data), callback.message.chat.id, callback.message.message_id,
                          parse_mode="html", disable_web_page_preview=True, reply_markup=markup)


def send_roles(message: types.Message):
    log_info(message)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Скрыть", callback_data='hide'))
    bot.send_message(message.chat.id, read_page('roles'), parse_mode='html', reply_markup=markup)


def send_guide(message: types.Message):
    log_info(message)
    if message.chat.type == 'supergroup':
        bot.reply_to(message, read_page('help'), parse_mode="html")
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Скрыть", callback_data='hide'))
    bot.send_message(message.chat.id, read_page('help'), parse_mode='html', reply_markup=markup)
    bot.delete_message(message.chat.id, message.message_id)


def admin_guide(message: types.Message):
    log_info(message)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Скрыть", callback_data="hide"))
    bot.send_message(message.chat.id, read_page('admin'), parse_mode="html", reply_markup=markup)
    bot.delete_message(message.chat.id, message.message_id)


def delete_button(callback: types.CallbackQuery):
    log_info(callback)
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
