import telebot
from telebot import BaseMiddleware, types

from sql_requests import create_user
from utils import check_permissions, detect_user, detect_chat
from config import events


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


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = 'is_admin'

    @staticmethod
    def check(message: types.Message):
        result = check_permissions(message, 5)
        if not result:
            print(f"[-]({detect_chat(message)}){detect_user(message)} don't have permissons 5: {message.text}")
        return result


class IsHeadman(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = 'is_headman'

    @staticmethod
    def check(message: types.Message):
        result = check_permissions(message, 4)
        if not result:
            print(f"[-]{detect_chat(message)}{detect_user(message)} don't have permissons 4: {message.text}")
        return result


class IsEditor(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = 'is_editor'

    @staticmethod
    def check(message: types.Message):
        result = check_permissions(message, 3)
        if not result:
            print(f"[-]{detect_chat(message)}{detect_user(message)} don't have permissons 3: {message.text}")
        return result


class IsClassmate(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_classmate'

    @staticmethod
    def check(message: types.Message):
        result = check_permissions(message, 1)
        if not result:
            print(f"[-]{detect_chat(message)}{detect_user(message)} don't have permissons 1: {message.text}")
        return result


class IsAllowed(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_allowed'

    @staticmethod
    def check(message: types.Message):
        result = check_permissions(message, 0)
        if not result:
            print(f"[-]{detect_chat(message)}{detect_user(message)} don't have permissons 0: {message.text}")
        return result


class ContainsEventWord(telebot.custom_filters.SimpleCustomFilter):
    key = 'has_event_word'

    @staticmethod
    def check(message: types.Message):
        check_list = list(events['text'].items())
        for item in check_list:
            if item[0] in message.text.lower():
                return True
        return False
