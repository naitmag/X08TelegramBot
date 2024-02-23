from telebot.handler_backends import StatesGroup, State


class TeachersRequestState(StatesGroup):
    request = State()


class LessonsRequestState(StatesGroup):
    get_week = State()
    get_day_of_the_week = State()
    get_lesson_number = State()
    get_lesson_name = State()
    get_lesson_type = State()
    get_teacher = State()
    confirm_input = State()
