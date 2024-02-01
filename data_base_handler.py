import telebot
import sqlite3
from shared import *


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
    max_age_difference = 100
    conn = sqlite3.connect("main_database.db")
    c = conn.cursor()

    c.execute("SELECT age, preferences FROM users WHERE user_id=?", (id,))
    result = c.fetchone()
    if result is None:
        conn.close()
        return []

    user_age, preferences = int(result[0]), result[1]
    users_ids_for_search = []

    if preferences == "Все":
        preferences = ("Девушка", "Парень")
    else:
        preferences = (preferences,)

    query = """
    SELECT user_id FROM users 
    WHERE age BETWEEN ? AND ? AND user_id != ? AND gender IN ({})
    """.format(
        ",".join("?" * len(preferences))
    )

    for x in range(1, max_age_difference + 1):
        params = [user_age - x, user_age + x, id] + list(preferences)
        c.execute(query, params)
        users_ids_for_search.extend([user[0] for user in c.fetchall()])
        
    print("before:",len(users_ids_for_search))

    
    user_ids_for_match = tuple((item for item in users_ids_for_search if item not in done_for_search))
    print("after:", len(user_ids_for_match))

    if not users_ids_for_search:
        done_for_search.clear()

    

        

    conn.close()
    return user_ids_for_match
