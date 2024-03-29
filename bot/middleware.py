import logging
import traceback

import telebot
from telebot import BaseMiddleware, types

from sql_requests import create_user


class ExceptionHandler(telebot.ExceptionHandler):
    def __init__(self, logger: logging.RootLogger):
        self.logger = logger

    def handle(self, exception):
        print(f"[!]MIDDLEWARE EXCEPTION: \"{exception}\". Check logs for details.")
        self.logger.error(f"{''.join(traceback.format_exception(exception))}")
        return True


class Middleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.update_types = ['message', 'callback_query']

    def pre_process(self, request: types.Message | types.CallbackQuery, data):
        create_user(request.from_user.id, request.from_user.first_name, request.from_user.last_name,
                    request.from_user.username)

    def post_process(self, message, data, exception=None):
        pass
