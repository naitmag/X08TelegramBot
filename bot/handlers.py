from telebot import types

from config import cabinets_info, bot


def manage_cabs(message: types.Message):
    args = message.text.split()
    if len(args) != 1:
        cabinets_info["cabinets"] = args[1:]
        cabinets_info[
            "author"] = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    if cabinets_info["cabinets"]:

        bot_reply = "<b>Кабинеты:</b>\n" + "\n".join(cabinets_info["cabinets"])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Кто прислал", callback_data="author"))
        bot.send_message(message.chat.id, bot_reply, parse_mode="html", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "<b>Кабинеты не добавлены</b>", parse_mode="html")

    bot.delete_message(message.chat.id, message.message_id)


def show_author(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id, f"Прислал: {cabinets_info['author']}", show_alert=True)
