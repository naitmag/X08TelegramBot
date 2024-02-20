import threading

from background import bot_background
from config import bot
from start import on_start


def main():
    other_action_thread = threading.Thread(target=bot_background)
    other_action_thread.start()

    on_start()
    print("[+]BOT STARTED")
    bot.polling()


if __name__ == '__main__':
    main()
