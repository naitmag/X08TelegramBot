from telebot import types

from config import cabinets_info, bot, schedule
from utils import send_schedule, get_schedule, send_weather

days = ("пн", "вт", "ср", "чт", "пт", "сб")


def manage_cabs(message: types.Message):

    author = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    args = message.text.split()[1:5]
    print(f"[=]{author} CABINETS REQUEST {args}")
    args = [i[:4] for i in args if len(i) >= 3 and i[:3].isdigit()]

    if len(args) > 0:
        cabinets_info["cabinets"] = args
        cabinets_info[
            "author"] = author
    if cabinets_info["cabinets"]:

        bot_reply = "<b>Кабинеты:</b>\n" + "\n".join(cabinets_info["cabinets"])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Кто прислал", callback_data="author"))
        bot.send_message(message.chat.id, bot_reply, parse_mode="html", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "<b>Кабинеты не добавлены</b>", parse_mode="html")

    bot.delete_message(message.chat.id, message.message_id)


def reply_schedule(message: types.Message):
    args = message.text.split()[1:3]
    args.extend([''] * (2 - len(args)))
    week = list(filter(lambda x: x.isdigit(), args))
    week = int(week[0]) if week else None
    day_of_week = list(filter(lambda x: x in days, args))
    day_of_week = days.index(day_of_week[0]) if day_of_week else None

    send_schedule(week, day_of_week, message.chat.id)

    bot.delete_message(message.chat.id, message.message_id)


def show_author(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id, f"Прислал: {cabinets_info['author']}", show_alert=True)


def scroll_schedule(callback: types.CallbackQuery):
    print(f"[=]@{callback.from_user.username if callback.from_user.username else callback.from_user.first_name} SCROLLS THROUGH THE SCHEDULE")
    week = int(callback.message.text.split()[4])
    week = week+1 if callback.data == "next" else week-1
    bot.edit_message_text(get_schedule(schedule, week),callback.message.chat.id, callback.message.message_id, parse_mode="html", reply_markup=callback.message.reply_markup)


def weather_request(message: types.Message):
    print(f"[=]@{message.from_user.username if message.from_user.username else message.from_user.first_name} REQUESTED WEATHER")
    send_weather(message.chat.id)
    bot.delete_message(message.chat.id,message.message_id)