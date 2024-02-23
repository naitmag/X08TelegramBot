import os
import time

from telebot import types

from config import pages, bot, ADMIN_ID
from utils import detect_user, print_feedback


def start_greetings(message: types.Message):
    print_feedback(message, 'started the bot')

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Команды", callback_data="help")
    button2 = types.InlineKeyboardButton("Роли", callback_data="roles")
    markup.row(button1, button2)
    markup.add(types.InlineKeyboardButton("Контакты", callback_data="contacts"))

    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'img', 'pages',
                              'start.jpg')
    with open(image_path, 'rb') as image:
        bot.send_photo(message.chat.id, image, pages["home"][0], parse_mode='html')

    time.sleep(1)
    bot.send_message(message.chat.id, pages["home"][1], parse_mode="html", reply_markup=markup)
    time.sleep(1)
    bot.send_message(ADMIN_ID, f"{detect_user(message)} запустил бота")


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


def delete_button(callback: types.CallbackQuery):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
