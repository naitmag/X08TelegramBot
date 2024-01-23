import threading

from config import bot
from handlers import manage_cabs, show_author
from background import bot_background


def main():
    other_action_thread = threading.Thread(target=bot_background)
    other_action_thread.start()

    bot.register_message_handler(manage_cabs, content_types=['text'],
                                 func=lambda message: message.text.lower().startswith("каб"))
    bot.register_callback_query_handler(show_author, func=lambda callback: callback.data == "author")

    bot.polling()


if __name__ == '__main__':
    main()
