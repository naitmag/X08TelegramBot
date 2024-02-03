import sqlite3 as sq


def create_user(telegram_id: int, name: str, lastname: str, username: str):
    with sq.connect('data/users.db') as con:
        cur = con.cursor()
        cur.execute(f"""INSERT INTO users (name,lastname,username,telegram_id)
                        VALUES ('{name}', '{lastname}', '{username}', {telegram_id})""")


def update_user_level(request, level):
    with sq.connect('data/users.db') as con:
        cur = con.cursor()
        data = cur.execute(
            f"""UPDATE users SET level = {level} WHERE username = '{request}' OR telegram_id = '{request}';""")
    return data


def get_user(telegram_id: int) -> list:
    with sq.connect('data/users.db') as con:
        cur = con.cursor()
        data = cur.execute(f"""SELECT * FROM users WHERE telegram_id == {telegram_id} LIMIT 1""")
    data = data.fetchall()

    return data[0] if data else []


def drop_database():
    with sq.connect('data/lessons.db') as con:
        cur = con.cursor()
        cur.execute("""DELETE FROM lessons""")


def read_txt():
    with open('data/lessons.txt', encoding='utf-8') as file:
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
    with sq.connect('data/lessons.db') as con:
        cur = con.cursor()

        if day_of_the_week is None:
            data = cur.execute(
                f"""SELECT * FROM lessons WHERE start <= {week} AND end >= {week} ORDER BY day_of_the_week ASC""")

        else:
            data = cur.execute(
                f"""SELECT * FROM lessons WHERE start <= {week} AND end >= {week} AND day_of_the_week == {day_of_the_week} ORDER BY day_of_the_week ASC""")

    return data.fetchall()


def get_teacher(request) -> list:
    with sq.connect('data/lessons.db') as con:
        cur = con.cursor()

        data = cur.execute(
            f"""SELECT * FROM lessons WHERE name LIKE '%{request[1:]}%' OR teacher like '%{request[1:]}%'""")
    return data.fetchall()


def create_lesson(interval: str, day_of_the_week: int, lesson_number: int, name: str, lesson_type: str = '-',
                  teacher: str = '-'):
    interval = interval.split('-')
    start = interval[0]
    end = interval[0] if len(interval) <= 1 else interval[1]

    with sq.connect('data/lessons.db') as con:
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
