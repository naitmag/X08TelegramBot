from telebot import BaseMiddleware, types

from sql_requests import create_user


class Middleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.update_types = ['message', 'callback_query']

    def pre_process(self, message: types.Message, data):
        data['user_id'] = message.from_user.id
        data['name'] = message.from_user.first_name
        data['lastname'] = message.from_user.last_name
        data['username'] = message.from_user.username
        create_user(data['user_id'], data['name'], data['lastname'], data['username'])

    def post_process(self, message, data, exception=None):
        if exception:
            print(f"[!]MIDDLEWARE ERROR: {exception}")
        return
