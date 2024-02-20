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
    # Class will check whether the user is admin or not
    key = 'is_admin'

    @staticmethod
    def check(request: types.Message | types.CallbackQuery):
        access = check_permissions(request, 5)
        if not access:
            if type(request) is types.Message:
                action = request.text
            else:
                action = request.data
            print(f"[-]{detect_chat(request)}{detect_user(request)} don't have permissons 3: {action}")
        return access


class IsHeadman(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is headman or not
    key = 'is_headman'

    @staticmethod
    def check(request: types.Message | types.CallbackQuery):
        access = check_permissions(request, 4)
        if not access:
            if type(request) is types.Message:
                action = request.text
            else:
                action = request.data
            print(f"[-]{detect_chat(request)}{detect_user(request)} don't have permissons 3: {action}")
        return access


class IsEditor(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is editor or not
    key = 'is_editor'

    @staticmethod
    def check(request: types.Message | types.CallbackQuery):
        access = check_permissions(request, 3)
        if not access:
            if type(request) is types.Message:
                action = request.text
            else:
                action = request.data
            print(f"[-]{detect_chat(request)}{detect_user(request)} don't have permissons 3: {action}")
        return access


class IsClassmate(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is classmate or not
    key = 'is_classmate'

    @staticmethod
    def check(request: types.Message | types.CallbackQuery):
        access = check_permissions(request, 1)
        if not access:
            if type(request) is types.Message:
                action = request.text
            else:
                action = request.data
            print(f"[-]{detect_chat(request)}{detect_user(request)} don't have permissons 3: {action}")
        return access


class IsAllowed(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user has access or not
    key = 'is_allowed'

    @staticmethod
    def check(request: types.Message | types.CallbackQuery):
        access = check_permissions(request, 0)
        if not access:
            if type(request) is types.Message:
                action = request.text
            else:
                action = request.data
            print(f"[-]{detect_chat(request)}{detect_user(request)} don't have permissons 3: {action}")
        return access


class ContainsEventWord(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the message contains the event word
    key = 'has_event_word'

    @staticmethod
    def check(message: types.Message):
        check_list = list(events['text'].items())
        for item in check_list:
            if item[0] in message.text.lower():
                return True
        return False
