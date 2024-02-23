import telebot
from telebot import types

from config import events
from utils import check_permissions


class Role(telebot.custom_filters.SimpleCustomFilter):

    def __init__(self, key: str, permission_level: int):
        self.key = key
        self.permission_level = permission_level

    def check(self, request: types.Message | types.CallbackQuery):
        return check_permissions(request, self.permission_level)


class IsAdmin(Role):

    def __init__(self):
        super().__init__('is_admin', 5)


class IsHeadman(Role):
    def __init__(self):
        super().__init__('is_headman', 4)


class IsEditor(Role):
    def __init__(self):
        super().__init__('is_editor', 3)


class IsClassmate(Role):
    def __init__(self):
        super().__init__('is_classmate', 1)


class IsAllowed(Role):
    def __init__(self):
        super().__init__('is_allowed', 0)


class ContainsEventWord(telebot.custom_filters.SimpleCustomFilter):
    key = 'has_event_word'

    def check(self, message: types.Message):
        check_list = list(events['text'].items())
        for word in check_list:
            if word[0] in message.text.lower():
                return True
        return False
