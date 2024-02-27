import telebot
from telebot import types

from config import bot, GROUP_ID, days
from utils import format_schedule, get_current_week, log_info, log_warn


def send_schedule(message: types.Message = None):
    if not message:
        bot.send_message(GROUP_ID, format_schedule(), parse_mode='html')
        return

    args = message.text.split()[1:3]

    log_info(message, f"requested schedule: {args}")

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


def scroll_schedule(callback: types.CallbackQuery):
    week = int(callback.message.text.split()[4])
    week = week - (-1 if callback.data == 'next' else 1)
    week = (week - 1 if week == 0 else week) % 21

    log_info(callback, 'scrolls schedule')
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
            log_warn(callback, 'TO MANY CALLBACK REQUESTS')


def scroll_current_week(callback: types.CallbackQuery):
    log_info(callback, "sets schedule to current week")
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("◀️", callback_data="back"),
               types.InlineKeyboardButton("▶️", callback_data="next"))

    bot.edit_message_text(format_schedule(get_current_week()), callback.message.chat.id, callback.message.message_id,
                          parse_mode='html', reply_markup=markup)
