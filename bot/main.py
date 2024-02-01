import threading

from config import bot
from handlers import manage_cabs, show_author, reply_schedule, scroll_schedule, weather_request, add_lessons_request, \
    raw_lessons_request, random_request, teachers_request, get_user_id, wrong_chat_type, start_greetings, send_contacts, \
    send_guide, contacts_button, guide_button, delete_button
from background import bot_background


def main():
    print("[+]BOT STARTED")
    other_action_thread = threading.Thread(target=bot_background)
    other_action_thread.start()

    bot.register_message_handler(raw_lessons_request, commands=['raw'], chat_types=['private'])
    bot.register_message_handler(send_contacts, commands=['contacts'], chat_types=['private'])
    bot.register_message_handler(start_greetings, commands=['start'], chat_types=['private'])

    bot.register_message_handler(wrong_chat_type,
                                 commands=['schedule', 'weather', 'cabinets', 'add', 'teacher'],
                                 chat_types=['private'])
    bot.register_message_handler(wrong_chat_type,
                                 commands=['start', 'contacts'],
                                 chat_types=['supergroup'])

    bot.register_message_handler(reply_schedule, commands=['schedule', 's'], chat_types=['supergroup'])
    bot.register_message_handler(weather_request, commands=['weather', 'w'], chat_types=['supergroup'])
    bot.register_message_handler(manage_cabs, commands=['cabinets', 'c'], chat_types=['supergroup'])
    bot.register_message_handler(add_lessons_request, commands=['add'], chat_types=['supergroup'])
    bot.register_message_handler(teachers_request, commands=['teacher', 't'], chat_types=['supergroup'])

    bot.register_message_handler(random_request, commands=['random', 'r'])
    bot.register_message_handler(get_user_id, commands=['id'])
    bot.register_message_handler(send_guide, commands=['help'])

    bot.register_message_handler(manage_cabs, content_types=['text'],
                                 func=lambda message: message.text.lower().startswith("каб"), chat_types=['supergroup'])

    bot.register_callback_query_handler(guide_button, func=lambda callback: callback.data == "help")
    bot.register_callback_query_handler(contacts_button, func=lambda callback: callback.data == "contacts")
    bot.register_callback_query_handler(delete_button, func=lambda callback: callback.data == "hide")
    bot.register_callback_query_handler(show_author, func=lambda callback: callback.data == "author")
    bot.register_callback_query_handler(scroll_schedule, func=lambda callback: callback.data == "next")
    bot.register_callback_query_handler(scroll_schedule, func=lambda callback: callback.data == "back")

    bot.polling()


if __name__ == '__main__':
    main()
