from telebot import types

import bot.config as config
from bot.config import bot, ADMIN_ID, roles
from bot.sql_requests import update_user_level, get_user
from bot.utils import log_info


def switch_admin_mode(message: types.Message):
    log_info(message)
    if message.from_user.id == ADMIN_ID:
        config.admin_mode = not config.admin_mode
        bot.send_message(message.chat.id, f"🔐 Режим админа теперь: {config.admin_mode} /am")
        bot.delete_message(message.chat.id, message.message_id)


def set_permission(message: types.Message):
    log_info(message)
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

    bot.delete_message(message.chat.id, message.message_id)


def show_permission(message: types.Message):
    log_info(message)
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
