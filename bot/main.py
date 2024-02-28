from threading import Thread

from background import background
from config import bot, logger
from start import on_start


def main():
    on_start()

    bot_background = Thread(target=background)
    bot_background.start()

    print('[+]BOT STARTED')
    logger.info('Bot started')
    bot.polling()


if __name__ == '__main__':
    main()
