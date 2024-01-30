import telebot
import sqlite3
from shared import user_data_dict


def save_to_db(user_id: int) -> None:
    user_data = user_data_dict.get(user_id, [])
    print(user_data)

    if len(user_data) == 8:
        conn = sqlite3.connect("main_database.db")
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                user_name TEXT,
                age TEXT,
                gender TEXT,
                preferences TEXT,
                user_info TEXT,
                user_place TEXT,
                image_link TEXT
            )
        """
        )

        c.execute(
            "INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?)", tuple(user_data)
        )
        conn.commit()
        conn.close()
    else:
        print("Ошибка: user_data не содержит необходимое количество элементов")


def get_user(user_id: str, get_user_info=True) -> tuple or bool:
    conn = sqlite3.connect("main_database.db")
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    user_name TEXT,
    age TEXT,
    gender TEXT,
    preferences TEXT,
    user_info TEXT,
    user_place TEXT,
    image_link TEXT
    )
    """
    )
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))

    user_data = c.fetchone()

    conn.close()

    if get_user_info:
        return user_data
    else:
        return False if user_data else True


def search_for_user(id: str) -> list:
    x = 2
    max_age_difference = 100
    conn = sqlite3.connect("main_database.db")
    c = conn.cursor()

    c.execute("SELECT age,preferences from users WHERE user_id=?", (id,))
    result = c.fetchone()
    if result is None:
        conn.close()
        return []

    user_age, preferences = int(result[0]), result[1]
    users_for_search = []
    if preferences == 'Все':
        preferences = ('Девушка', 'Парень')
    while x <= max_age_difference:
        for preference in (preferences, ):
            print(preference)
            c.execute(
                "SELECT * from users WHERE age <= ? AND age >= ? AND user_id != ? AND gender = ?",
                (user_age + x, user_age - x, id, preference),
            )
            new_users = c.fetchall()
            users_for_search.extend(new_users)
        x += 1
        print(x)
    conn.close()
    return users_for_search
