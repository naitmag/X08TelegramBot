define_time = {
    0: "8:00",
    1: "9:35",
    2: "11:10",
    3: "13:00",
    4: "14:35"
}
define_week = {
    0: "🫨 Понедельник",
    1: "☕️ Вторник",
    2: "🪩 Среда",
    3: "🌟 Четверг",
    4: "🍻 Пятница",
    5: "🛌 Суббота"
}


def read_lessons(path: str) -> dict:
    with open(path, encoding='utf-8') as file:
        file = file.read()

    days = file.split('\n\n\n')

    day_of_the_week = 0
    lesson_number = 0
    schedule = {}
    for day in days:
        schedule[day_of_the_week] = {}
        for lesson in day.split('\n\n'):
            schedule[day_of_the_week][lesson_number] = lesson.split('\n')
            lesson_number += 1
        lesson_number = 0
        day_of_the_week += 1
    return schedule


def check_week(interval: str, week: int) -> False:
    args = tuple(map(int, interval.split("-")))
    if len(args) == 1:
        return args[0] == week
    return week in range(args[0], args[1] + 1)
