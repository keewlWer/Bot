import telebot
import sqlite3


def save_to_db(user_data: list) -> None:
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
    c.execute(""" INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?) """, user_data)
    conn.commit()
    conn.close()


def get_user(user_id: str, get_user_info=True) -> tuple or bool:
    conn = sqlite3.connect("main_database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))

    user_data = c.fetchone()

    conn.close()

    if get_user_info:
        return user_data
    else:
        return False if user_data else True
