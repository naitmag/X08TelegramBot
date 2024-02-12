import sqlite3 as sq
from pathlib import Path


def create_user(telegram_id: int, name: str, lastname: str, username: str):
    with sq.connect(f"{Path(__file__).parent.resolve()}/data/users.db") as con:
        cur = con.cursor()
        cur.execute(f"""INSERT OR IGNORE INTO users (name, lastname, username, telegram_id)
                SELECT '{name}', '{lastname}', '{username}', {telegram_id}
                WHERE NOT EXISTS (
                SELECT 1 FROM users WHERE telegram_id = {telegram_id} 
                );""")


def update_user_level(request, level):
    with sq.connect(f"{Path(__file__).parent.resolve()}/data/users.db") as con:
        cur = con.cursor()
        data = cur.execute(
            f"""UPDATE users SET level = {level} WHERE username = '{request}' OR telegram_id = '{request}';""")
    return data


def get_user(request: str or int) -> list:
    with sq.connect(f"{Path(__file__).parent.resolve()}/data/users.db") as con:
        cur = con.cursor()
        data = cur.execute(f"""SELECT * FROM users WHERE username = '{request}' OR telegram_id = '{request}'""")
    data = data.fetchall()

    return data[0] if data else []


def drop_database():
    with sq.connect(f"{Path(__file__).parent.resolve()}/data/lessons.db") as con:
        cur = con.cursor()
        cur.execute("""DELETE FROM lessons""")


def read_txt():
    with open(f"{Path(__file__).parent.resolve()}/data/lessons.txt", encoding='utf-8') as file:
        file = file.read()

        days = file.split('\n\n\n')

        day_of_the_week = 0
        lesson_number = 0
        for day in days:
            for lessons in day.split('\n\n'):
                for lesson in lessons.split("\n"):
                    if lesson != '-':
                        lesson = lesson.split()
                        lesson_type = lesson[1]
                        name = lesson[2].replace('_', ' ').capitalize()
                        teacher = ' '.join(lesson[3:])

                        create_lesson(lesson[0], day_of_the_week, lesson_number, name, lesson_type, teacher)

                lesson_number += 1
            lesson_number = 0
            day_of_the_week += 1


def get_schedule(week: int = None, day_of_the_week: int = None) -> list:
    with sq.connect(f"{Path(__file__).parent.resolve()}/data/lessons.db") as con:
        cur = con.cursor()

        if day_of_the_week is None:
            data = cur.execute(
                f"""SELECT * FROM lessons WHERE start <= {week} 
                AND end >= {week} 
                ORDER BY day_of_the_week, lesson_number ASC""")

        else:
            data = cur.execute(
                f"""SELECT * FROM lessons 
                WHERE start <= {week} 
                AND end >= {week} 
                AND day_of_the_week == {day_of_the_week} 
                ORDER BY day_of_the_week, lesson_number ASC""")

    return data.fetchall()


def get_teacher(request) -> list:
    with sq.connect(f"{Path(__file__).parent.resolve()}/data/lessons.db") as con:
        cur = con.cursor()

        data = cur.execute(
            f"""SELECT * FROM lessons WHERE name LIKE '%{request[1:]}%' OR teacher LIKE '%{request[1:]}%'""")
    return data.fetchall()


def create_lesson(interval: str, day_of_the_week: int, lesson_number: int, name: str, lesson_type: str = 'доп.',
                  teacher: str = 'преп. неизвестно'):
    interval = interval.split('-')
    start = interval[0]
    end = interval[0] if len(interval) <= 1 else interval[1]

    with sq.connect(f"{Path(__file__).parent.resolve()}/data/lessons.db") as con:
        cur = con.cursor()

        cur.execute(
            f"""INSERT OR IGNORE INTO lessons (day_of_the_week, lesson_number, type, name, start, end, teacher)
                SELECT {day_of_the_week}, {lesson_number}, '{lesson_type}', '{name}', {start},{end},'{teacher}'
                WHERE NOT EXISTS (
                SELECT 1 FROM lessons WHERE day_of_the_week = {day_of_the_week} 
                AND lesson_number = {lesson_number} 
                AND type ='{lesson_type}' 
                AND name='{name}' 
                AND start = {start}
                AND end = {end} 
                AND teacher ='{teacher}'
                );""")


def delete_lesson(day_of_the_week: int, lesson_number: int, name: str):
    with sq.connect(f"{Path(__file__).parent.resolve()}/data/lessons.db") as con:
        cur = con.cursor()
        data = cur.execute(
            f"""SELECT * FROM lessons WHERE 
            day_of_the_week == {day_of_the_week} 
            AND lesson_number == {lesson_number} 
            AND name LIKE '%{name[1:]}%'""")

        data = data.fetchall()
        if len(data) == 1:
            cur.execute(
                f"""DELETE FROM lessons WHERE 
                        day_of_the_week == {day_of_the_week} 
                        AND lesson_number == {lesson_number} 
                        AND name LIKE '%{name[1:]}%'""")

        return data
