from telebot import custom_filters

from handlers import admin, general, lessons, pages, schedule, user_requests
from config import bot
from filters import IsAdmin, IsHeadman, IsEditor, IsAllowed, IsClassmate, ContainsEventWord
from handlers.user_states import LessonsRequestState, TeachersRequestState
from middleware import Middleware
from utils import read_database, clear_database


def add_custom_filters():
    bot.add_custom_filter(IsAdmin())
    bot.add_custom_filter(IsHeadman())
    bot.add_custom_filter(IsEditor())
    bot.add_custom_filter(IsAllowed())
    bot.add_custom_filter(IsClassmate())
    bot.add_custom_filter(ContainsEventWord())
    bot.add_custom_filter(custom_filters.StateFilter(bot))


def register_callbacks():
    bot.register_callback_query_handler(user_requests.cancel_request, state='*',
                                        func=lambda callback: callback.data == 'cancel_request')
    bot.register_callback_query_handler(lessons.input_week, state=LessonsRequestState.get_week,
                                        func=lambda callback: callback.data in ['current_week', 'next_week'])
    bot.register_callback_query_handler(lessons.input_day_of_the_week, state=LessonsRequestState.get_day_of_the_week,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(lessons.input_lesson_number, state=LessonsRequestState.get_lesson_number,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(lessons.input_lesson_type, state=LessonsRequestState.get_lesson_type,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(lessons.confirm_lesson, state=LessonsRequestState.confirm_input,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(user_requests.update_weather,
                                        func=lambda callback: callback.data == "update_weather")
    bot.register_callback_query_handler(pages.home_page, func=lambda callback: callback.data == "home2")
    bot.register_callback_query_handler(pages.delete_button, func=lambda callback: callback.data == "hide")
    bot.register_callback_query_handler(pages.pages_button,
                                        func=lambda callback: callback.data in ["help", "contacts", "roles"])
    bot.register_callback_query_handler(user_requests.show_author, func=lambda callback: callback.data == "cabs_author")

    bot.register_callback_query_handler(schedule.scroll_schedule,
                                        func=lambda callback: callback.data in ["schedule_next", "schedule_back"],
                                        is_allowed=True)
    bot.register_callback_query_handler(schedule.scroll_current_week,
                                        func=lambda callback: callback.data == 'schedule_current_week',
                                        is_allowed=True)


def register_message_handlers():
    bot.register_message_handler(user_requests.send_teacher, state=TeachersRequestState.request)

    bot.register_message_handler(lessons.input_week, state=LessonsRequestState.get_week)

    bot.register_message_handler(lessons.input_lesson_name, state=LessonsRequestState.get_lesson_name)
    bot.register_message_handler(lessons.input_lesson_teacher, state=LessonsRequestState.get_teacher)

    bot.register_message_handler(pages.start_greetings, commands=['start'], chat_types=['private'])
    bot.register_message_handler(user_requests.random_request, commands=['random', 'r'], is_allowed=True)
    bot.register_message_handler(read_database, commands=['read'], chat_types=['private'], is_admin=True)
    bot.register_message_handler(clear_database, commands=['drop'], chat_types=['private'], is_admin=True)
    bot.register_message_handler(pages.admin_guide, commands=['admin'], chat_types=['private'])
    bot.register_message_handler(admin.switch_admin_mode, commands=['am'], chat_types=['private'])

    bot.register_message_handler(admin.set_permission, commands=['set'], is_admin=True)
    bot.register_message_handler(admin.show_permission, commands=['perm'], is_admin=True)

    bot.register_message_handler(user_requests.find_teachers, commands=['teacher', 't'], is_allowed=True)

    bot.register_message_handler(user_requests.send_weather, commands=['weather', 'w'], is_allowed=True)
    bot.register_message_handler(user_requests.manage_cabs, commands=['cabinets', 'c'], is_classmate=True)
    bot.register_message_handler(lessons.manage_lessons, commands=['add', 'remove'], is_editor=True)

    bot.register_message_handler(general.wrong_chat_type,
                                 commands=['start', 'admin'], chat_types=['supergroup'], is_allowed=True)

    bot.register_message_handler(schedule.send_schedule, commands=['schedule', 's'], is_allowed=True)
    bot.register_message_handler(general.send_id, commands=['id'])
    bot.register_message_handler(pages.send_guide, commands=['help'])
    bot.register_message_handler(pages.send_roles, commands=['roles'])

    bot.register_message_handler(user_requests.manage_cabs, content_types=['text'],
                                 func=lambda message: message.text.lower().startswith("каб"), is_classmate=True)

    bot.register_message_handler(general.check_photo_event, content_types=['photo'], chat_types=['supergroup'])
    bot.register_message_handler(general.check_text_event, content_types=['text'], chat_types=['supergroup'],
                                 has_event_word=True)


def on_start():
    bot.setup_middleware(Middleware())

    add_custom_filters()
    register_message_handlers()
    register_callbacks()
