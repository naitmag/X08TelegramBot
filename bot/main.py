import threading

from telebot import custom_filters

from background import bot_background
from config import bot
from handlers import manage_cabs, show_author, send_weather, \
    random_request, send_id, wrong_chat_type, start_greetings, \
    send_guide, pages_button, home_page, send_schedule, send_teacher, add_lessons, scroll_schedule, \
    set_permission, remove_lesson, admin_guide, show_permission, delete_button, switch_admin_mode, check_text_event, \
    check_photo_event, send_roles, TeachersRequestState, find_teachers, cancel_request, \
    input_week, AddLessonsRequestState, update_weather, input_day_of_the_week, input_lesson_number, input_lesson_type, \
    input_lesson_name, confirm_lesson, input_lesson_teacher
from user_processing_middleware import Middleware, IsAllowed, IsAdmin, IsEditor, IsHeadman, IsClassmate, \
    ContainsEventWord

from utils import clear_database, read_database


def main():
    print("[+]BOT STARTED")

    other_action_thread = threading.Thread(target=bot_background)
    other_action_thread.start()

    #bot.setup_middleware(Middleware())

    bot.add_custom_filter(IsAdmin())
    bot.add_custom_filter(IsHeadman())
    bot.add_custom_filter(IsEditor())
    bot.add_custom_filter(IsAllowed())
    bot.add_custom_filter(IsClassmate())
    bot.add_custom_filter(ContainsEventWord())
    bot.add_custom_filter(custom_filters.StateFilter(bot))

    bot.register_callback_query_handler(cancel_request, state='*',
                                        func=lambda callback: callback.data == 'cancel_request')

    bot.register_message_handler(send_teacher, state=TeachersRequestState.request)

    bot.register_message_handler(input_week, state=AddLessonsRequestState.get_week)
    bot.register_callback_query_handler(input_week, state=AddLessonsRequestState.get_week,
                                        func=lambda callback: callback.data in ['current_week', 'next_week'])
    bot.register_callback_query_handler(input_day_of_the_week, state=AddLessonsRequestState.get_day_of_the_week,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(input_lesson_number, state=AddLessonsRequestState.get_lesson_number,
                                        func=lambda callback: True)
    bot.register_callback_query_handler(input_lesson_type, state=AddLessonsRequestState.get_lesson_type,
                                        func=lambda callback: True)
    bot.register_message_handler(input_lesson_name, state=AddLessonsRequestState.get_lesson_name)
    bot.register_message_handler(input_lesson_teacher, state=AddLessonsRequestState.get_teacher)
    bot.register_callback_query_handler(confirm_lesson, state=AddLessonsRequestState.confirm_input,
                                        func=lambda callback: True)

    bot.register_message_handler(start_greetings, commands=['start'], chat_types=['private'])
    bot.register_message_handler(random_request, commands=['random', 'r'], chat_types=['private'], is_allowed=True)
    bot.register_message_handler(read_database, commands=['read'], chat_types=['private'], is_admin=True)
    bot.register_message_handler(clear_database, commands=['drop'], chat_types=['private'], is_admin=True)
    bot.register_message_handler(admin_guide, commands=['admin'], chat_types=['private'])
    bot.register_message_handler(switch_admin_mode, commands=['am'], chat_types=['private'])

    bot.register_message_handler(set_permission, commands=['set'], is_admin=True)
    bot.register_message_handler(show_permission, commands=['perm'], is_admin=True)

    bot.register_message_handler(find_teachers, commands=['teacher', 't'])

    bot.register_message_handler(send_weather, commands=['weather', 'w'], is_classmate=True)
    bot.register_message_handler(manage_cabs, commands=['cabinets', 'c'], is_classmate=True)
    bot.register_message_handler(add_lessons, commands=['add'], is_editor=True)
    bot.register_message_handler(remove_lesson, commands=['remove'], is_editor=True)
    bot.register_message_handler(random_request, commands=['random', 'r'], chat_types=['supergroup'], is_headman=True)

    bot.register_message_handler(wrong_chat_type,
                                 commands=['start', 'admin'], chat_types=['supergroup'], is_allowed=True)

    bot.register_message_handler(send_schedule, commands=['schedule', 's'])
    bot.register_message_handler(send_id, commands=['id'])
    bot.register_message_handler(send_guide, commands=['help'])
    bot.register_message_handler(send_roles, commands=['roles'])

    bot.register_message_handler(manage_cabs, content_types=['text'],
                                 func=lambda message: message.text.lower().startswith("каб"), is_classmate=True)

    bot.register_callback_query_handler(update_weather, func=lambda callback: callback.data == "update_weather")
    bot.register_callback_query_handler(home_page, func=lambda callback: callback.data == "home")
    bot.register_callback_query_handler(delete_button, func=lambda callback: callback.data == "hide")
    bot.register_callback_query_handler(pages_button,
                                        func=lambda callback: callback.data in ["help", "contacts", "roles"])
    bot.register_callback_query_handler(show_author, func=lambda callback: callback.data == "author")

    bot.register_callback_query_handler(scroll_schedule, func=lambda callback: callback.data in ["next", "back"],
                                        is_allowed=True)

    bot.register_message_handler(check_photo_event, content_types=['photo'], chat_types=['supergroup'])
    bot.register_message_handler(check_text_event, content_types=['text'], chat_types=['supergroup'],
                                 has_event_word=True)

    bot.polling()


if __name__ == '__main__':
    main()
