import threading

from config import bot
from handlers import manage_cabs, show_author, reply_schedule, scroll_schedule, weather_request
from background import bot_background


def main():
    print("[+]BOT STARTED")
    other_action_thread = threading.Thread(target=bot_background)
    other_action_thread.start()

    bot.register_message_handler(reply_schedule, commands=['schedule', 's'])
    bot.register_message_handler(weather_request, commands=['weather', 'w'])
    bot.register_message_handler(manage_cabs, commands=['cabinets', 'c'])

    bot.register_message_handler(manage_cabs, content_types=['text'],
                                 func=lambda message: message.text.lower().startswith("каб"))
    bot.register_callback_query_handler(show_author, func=lambda callback: callback.data == "author")
    bot.register_callback_query_handler(scroll_schedule, func=lambda callback: callback.data == "next" or "back")

    bot.polling()


if __name__ == '__main__':
    main()
