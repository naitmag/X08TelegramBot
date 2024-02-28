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
        data['user_id'] = request.from_user.id
        data['name'] = request.from_user.first_name
        data['lastname'] = request.from_user.last_name
        data['username'] = request.from_user.username
        create_user(data['user_id'], data['name'], data['lastname'], data['username'])

    def post_process(self, message, data, exception=None):
        pass
