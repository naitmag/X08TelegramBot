import threading

from background import bot_background
from config import bot
from handlers import manage_cabs, show_author, weather_request, \
    random_request, send_id, wrong_chat_type, start_greetings, send_contacts, \
    send_guide, pages_button, home_page, delete_button, send_schedule, send_teacher, add_lesson, scroll_schedule, \
    set_permission, remove_lesson
from user_processing_middleware import Middleware

from utils import clear_database, read_database


def main():
    print("[+]BOT 2 STARTED")

    other_action_thread = threading.Thread(target=bot_background)
    other_action_thread.start()

    bot.setup_middleware(Middleware())

    bot.register_message_handler(send_contacts, commands=['contacts'], chat_types=['private'])
    bot.register_message_handler(start_greetings, commands=['start'], chat_types=['private'])
    bot.register_message_handler(read_database, commands=['read'], chat_types=['private'])
    bot.register_message_handler(clear_database, commands=['drop'], chat_types=['private'])

    bot.register_message_handler(set_permission, commands=['perm'])

    bot.register_message_handler(wrong_chat_type,
                                 commands=['schedule', 'cabinets', 'add', 'teacher'],
                                 chat_types=['private'])
    bot.register_message_handler(wrong_chat_type,
                                 commands=['start', 'contacts'],
                                 chat_types=['supergroup'])

    bot.register_message_handler(send_schedule, commands=['schedule', 's'], chat_types=['supergroup'])
    bot.register_message_handler(weather_request, commands=['weather', 'w'], chat_types=['supergroup'])
    bot.register_message_handler(manage_cabs, commands=['cabinets', 'c'], chat_types=['supergroup'])
    bot.register_message_handler(add_lesson, commands=['add'], chat_types=['supergroup'])
    bot.register_message_handler(remove_lesson, commands=['remove'], chat_types=['supergroup'])
    bot.register_message_handler(send_teacher, commands=['teacher', 't'], chat_types=['supergroup'])

    bot.register_message_handler(random_request, commands=['random', 'r'])
    bot.register_message_handler(send_id, commands=['id'])
    bot.register_message_handler(send_guide, commands=['help'])

    bot.register_message_handler(manage_cabs, content_types=['text'],
                                 func=lambda message: message.text.lower().startswith("каб"), chat_types=['supergroup'])

    bot.register_callback_query_handler(home_page, func=lambda callback: callback.data == "home")
    bot.register_callback_query_handler(pages_button, func=lambda callback: callback.data in ["help", "contacts"])
    bot.register_callback_query_handler(delete_button, func=lambda callback: callback.data == "hide")
    bot.register_callback_query_handler(show_author, func=lambda callback: callback.data == "author")
    bot.register_callback_query_handler(scroll_schedule, func=lambda callback: callback.data in ["next", "back"])

    bot.polling()


if __name__ == '__main__':
    main()
