from telebot import custom_filters

from config import bot
from handlers import cancel_request, input_week, LessonsRequestState, input_day_of_the_week, input_lesson_number, \
    input_lesson_type, confirm_lesson, update_weather, home_page, delete_button, pages_button, show_author, \
    scroll_schedule, send_teacher, TeachersRequestState, input_lesson_name, input_lesson_teacher, start_greetings, \
    random_request, admin_guide, switch_admin_mode, set_permission, show_permission, find_teachers, send_weather, \
    manage_cabs, manage_lessons, wrong_chat_type, send_schedule, send_id, send_guide, send_roles, \
    check_text_event, check_photo_event
from user_processing_middleware import Middleware, IsAdmin, IsHeadman, IsEditor, IsAllowed, IsClassmate, \
    ContainsEventWord
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
    bot.register_callback_query_handler(cancel_request, state='*',
                                        func=lambda callback: callback.data == 'cancel_request')
    bot.register_callback_query_handler(input_week, state=LessonsRequestState.get_week,
                                        func=lambda callback: callback.data in ['current_week', 'next_week'])
    bot.register_callback_query_handler(input_day_of_the_week, state=LessonsRequestState.get_day_of_the_week,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(input_lesson_number, state=LessonsRequestState.get_lesson_number,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(input_lesson_type, state=LessonsRequestState.get_lesson_type,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(confirm_lesson, state=LessonsRequestState.confirm_input,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(update_weather, func=lambda callback: callback.data == "update_weather")
    bot.register_callback_query_handler(home_page, func=lambda callback: callback.data == "home")
    bot.register_callback_query_handler(delete_button, func=lambda callback: callback.data == "hide")
    bot.register_callback_query_handler(pages_button,
                                        func=lambda callback: callback.data in ["help", "contacts", "roles"])
    bot.register_callback_query_handler(show_author, func=lambda callback: callback.data == "author")

    bot.register_callback_query_handler(scroll_schedule, func=lambda callback: callback.data in ["next", "back"],
                                        is_allowed=True)


def register_message_handlers():
    bot.register_message_handler(send_teacher, state=TeachersRequestState.request)

    bot.register_message_handler(input_week, state=LessonsRequestState.get_week)

    bot.register_message_handler(input_lesson_name, state=LessonsRequestState.get_lesson_name)
    bot.register_message_handler(input_lesson_teacher, state=LessonsRequestState.get_teacher)

    bot.register_message_handler(start_greetings, commands=['start'], chat_types=['private'])
    bot.register_message_handler(random_request, commands=['random', 'r'], is_allowed=True)
    bot.register_message_handler(read_database, commands=['read'], chat_types=['private'], is_admin=True)
    bot.register_message_handler(clear_database, commands=['drop'], chat_types=['private'], is_admin=True)
    bot.register_message_handler(admin_guide, commands=['admin'], chat_types=['private'])
    bot.register_message_handler(switch_admin_mode, commands=['am'], chat_types=['private'])

    bot.register_message_handler(set_permission, commands=['set'], is_admin=True)
    bot.register_message_handler(show_permission, commands=['perm'], is_admin=True)

    bot.register_message_handler(find_teachers, commands=['teacher', 't'], is_allowed=True)

    bot.register_message_handler(send_weather, commands=['weather', 'w'], is_allowed=True)
    bot.register_message_handler(manage_cabs, commands=['cabinets', 'c'], is_classmate=True)
    bot.register_message_handler(manage_lessons, commands=['add', 'remove'], is_editor=True)

    bot.register_message_handler(wrong_chat_type,
                                 commands=['start', 'admin'], chat_types=['supergroup'], is_allowed=True)

    bot.register_message_handler(send_schedule, commands=['schedule', 's'], is_allowed=True)
    bot.register_message_handler(send_id, commands=['id'])
    bot.register_message_handler(send_guide, commands=['help'])
    bot.register_message_handler(send_roles, commands=['roles'])

    bot.register_message_handler(manage_cabs, content_types=['text'],
                                 func=lambda message: message.text.lower().startswith("каб"), is_classmate=True)

    bot.register_message_handler(check_photo_event, content_types=['photo'], chat_types=['supergroup'])
    bot.register_message_handler(check_text_event, content_types=['text'], chat_types=['supergroup'],
                                 has_event_word=True)


def on_start():
    bot.setup_middleware(Middleware())

    add_custom_filters()
    register_message_handlers()
    register_callbacks()
