import os
import telebot
from data_base_handler import save_to_db, get_user, search_for_user
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re
from dotenv import load_dotenv
import sqlite3
from shared import user_data_dict


GENDER_OPTIONS = ["Девушка", "Парень", 'Все']
USER_OPTIONS_YN = ["Да", "Нет"]
DEFAULT_ERROR_TEMPLATES = {
    "common": "Произошла ошибка",
    "oneMoreTry": "попробуйте снова ввести",
}
SMILES = {"heart_smile": "\u2764\uFE0F", "ghost_smile": "\U0001F47B"}
MEDIA_FILE_PATH = ""
#LIST_OF_USER_DATA = []
user_numbers = {} 

SET_OF_NUMBERS_STR = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "0"}

load_dotenv()
bot_token = os.environ["bot_token"]
bot = telebot.TeleBot(bot_token)


def process_username(message: telebot.types.Message) -> None:
    user_name = message.text
    user_id = message.from_user.id
    if user_id not in user_data_dict:
        user_data_dict[user_id] = [user_id]
    if user_name:
        user_data_dict[user_id].append(user_name)
        print (user_data_dict)
        msg = bot.send_message(
            message.chat.id, f"{user_name.capitalize()}, введите свой возраст"
        )
        bot.register_next_step_handler(msg, process_age)
    else:
        msg = bot.send_message(
            message.chat.id, f'{DEFAULT_ERROR_TEMPLATES["common"]}, введите имя еще раз'
        )
        bot.register_next_step_handler(msg, process_username)


def process_age(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    age = message.text
    if age and (set(age) <= SET_OF_NUMBERS_STR) and 14 < int(age) < 1000:
        user_data_dict[user_id].append(age)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = KeyboardButton(GENDER_OPTIONS[0])
        btn2 = KeyboardButton(GENDER_OPTIONS[1])
        markup.row(btn1, btn2)
        msg = bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_gender)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'{DEFAULT_ERROR_TEMPLATES["common"]}, {DEFAULT_ERROR_TEMPLATES["oneMoreTry"]} возраст',
        )
        bot.register_next_step_handler(msg, process_age)


def process_gender(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    gender = message.text
    if gender == GENDER_OPTIONS[0] or gender == GENDER_OPTIONS[1]:
        user_data_dict[user_id].append(gender)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = KeyboardButton(GENDER_OPTIONS[0])
        btn2 = KeyboardButton(GENDER_OPTIONS[1])
        btn3 = KeyboardButton(GENDER_OPTIONS[2])
        markup.row(btn1, btn2, btn3)
        msg = bot.send_message(
            message.chat.id, "Выберите пол просматриваемых анкет", reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_preferences)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'{DEFAULT_ERROR_TEMPLATES["common"]}, {DEFAULT_ERROR_TEMPLATES["oneMoreTry"]} свой пол',
        )
        bot.register_next_step_handler(msg, process_gender)


def process_preferences(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    markup = ReplyKeyboardRemove()
    user_preferences = message.text
    if (
        user_preferences == GENDER_OPTIONS[0]
        or user_preferences == GENDER_OPTIONS[1]
        or user_preferences == GENDER_OPTIONS[2]
    ):
        user_data_dict[user_id].append(user_preferences)
        info = bot.send_message(
            message.chat.id, text="Напишите что-нибудь о себе", reply_markup=markup
        )
        bot.register_next_step_handler(info, process_user_info)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'{DEFAULT_ERROR_TEMPLATES["common"]}, {DEFAULT_ERROR_TEMPLATES["oneMoreTry"]} свои предпочтения',
        )
        bot.register_next_step_handler(msg, process_preferences)


def process_user_info(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    user_info = message.text
    if user_info:
        user_data_dict[user_id].append(user_info)
        place = bot.send_message(message.chat.id, text="Откуда вы?")
        bot.register_next_step_handler(place, process_place)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'{DEFAULT_ERROR_TEMPLATES["common"]}, {DEFAULT_ERROR_TEMPLATES["oneMoreTry"]} информацию о пользователе',
        )
        bot.register_next_step_handler(msg, process_user_info)


def process_place(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    user_place = message.text
    if user_place and user_place == re.sub("[*#0-9]", "", user_place):
        user_data_dict[user_id].append(user_place)
        msg = bot.send_message(message.chat.id, text="Отправьте свое фото")
        bot.register_next_step_handler(msg, process_image)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'{DEFAULT_ERROR_TEMPLATES["common"]}, {DEFAULT_ERROR_TEMPLATES["oneMoreTry"]} свое местоположение',
        )
        bot.register_next_step_handler(msg, process_place)


def process_image(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    global MEDIA_FILE_PATH, user_data_dict
    try:
        photo_file = bot.get_file(message.photo[-1].file_id)
        if photo_file:
            downloaded_file = bot.download_file(photo_file.file_path)

            MEDIA_FILE_PATH = f"images/{photo_file.file_id}.jpg"
            user_data_dict[user_id].append(MEDIA_FILE_PATH)

            with open(MEDIA_FILE_PATH, "wb") as file:
                file.write(downloaded_file)

            with open(MEDIA_FILE_PATH, "rb") as file:
                user_data = user_data_dict.get(user_id, [])
                if user_data:
                    if len(user_data) > 6:
                        caption = f"{user_data[1]}, {user_data[2]}, {user_data[6]} - {user_data[5]}"
                        bot.send_photo(
                            message.chat.id,
                            file,
                            caption=caption,)

            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = KeyboardButton(USER_OPTIONS_YN[0])
            btn2 = KeyboardButton(USER_OPTIONS_YN[1])
            markup.row(btn1, btn2)
            bot.send_message(
                message.chat.id, f"Вот ваша анкета! Идем дальше?", reply_markup=markup
            )
            bot.register_next_step_handler(message, redirect_user_to_start)

        else:
            msg = bot.send_message(
                message.chat.id,
                f'{DEFAULT_ERROR_TEMPLATES["common"]} при обработке фото, попробуйте отправить фото еще раз',
            )
            bot.register_next_step_handler(msg, process_image)

    except Exception as e:
        bot.send_message(
            message.chat.id, f"{DEFAULT_ERROR_TEMPLATES[0]}: {type(e).__name__}, {e}"
        )
        user_data_dict.pop(user_id, None)
        bot.register_next_step_handler(message, process_username)


def redirect_user_to_start(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    global user_data_dict
    reply = message.text
    if reply == USER_OPTIONS_YN[1]:
        if MEDIA_FILE_PATH:
            try:
                os.remove(MEDIA_FILE_PATH)
            except FileNotFoundError:
                print(f"Файл не найден: {MEDIA_FILE_PATH}")
            except Exception as e:
                print(f"Ошибка при удалении файла: {e}")
        user_data_dict.pop(user_id, None)
        print(user_data_dict)
        markup = ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, "Введите имя", reply_markup=markup)
        bot.register_next_step_handler(msg, process_username)
    elif reply == USER_OPTIONS_YN[0]:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = KeyboardButton("Начать поиск")
        btn2 = KeyboardButton("Моя анкета")
        btn3 = KeyboardButton("Посмотреть кто меня лайкнул")
        btn4 = KeyboardButton("Режим рандомной переписки")
        btn5 = KeyboardButton("Не хочу никого искать")
        btn6 = KeyboardButton("Отправить донат разработчикам:)")
        markup.row(btn1, btn2, btn3)
        markup.row(btn4, btn5, btn6)
        msg = bot.send_message(message.chat.id, "Выберите действие?", reply_markup=markup)
        print(user_data_dict)
        save_to_db(user_id)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'Выберите "{USER_OPTIONS_YN[0]}" или "{USER_OPTIONS_YN[1]}"',
        )
        bot.register_next_step_handler(msg, redirect_user_to_start)
        

@bot.message_handler(func=lambda message: message.text == "Вернуться в меню")
def user_options(message: telebot.types.Message) -> None:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("Начать поиск")
    btn2 = KeyboardButton("Моя анкета")
    btn3 = KeyboardButton("Посмотреть кто меня лайкнул")
    btn4 = KeyboardButton("Режим рандомной переписки")
    btn5 = KeyboardButton("Не хочу никого искать")
    btn6 = KeyboardButton("Отправить донат разработчикам:)")
    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)
    msg = bot.send_message(message.chat.id, "Выберите действие?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Начать поиск" or message.text in [SMILES['heart_smile'], SMILES['ghost_smile']])
def search_for_profiles(message: telebot.types.Message) -> None:
    user_id = message.chat.id
    msg = message.text
    list_of_users = search_for_user(str(user_id))

    if user_id not in user_numbers:
        user_numbers[user_id] = 0

    user_number = user_numbers[user_id]

    if msg == "Начать поиск":
        if not list_of_users:
            bot.send_message(message.chat.id, "Ничего не найдено")
        else:
            send_user_profile(message, list_of_users, user_number)

    elif msg in [SMILES['heart_smile'], SMILES['ghost_smile']]:

        if user_number < len(list_of_users):
            send_user_profile(message, list_of_users, user_number)

    user_numbers[user_id] = (user_number + 1) % len(list_of_users)

def send_user_profile(message, list_of_users, user_number):
    with open(f"{list_of_users[user_number][7]}", "rb") as file:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = KeyboardButton(SMILES['heart_smile'])
        btn2 = KeyboardButton(SMILES['ghost_smile'])
        btn3 = KeyboardButton('Вернуться в меню')
        markup.row(btn1, btn2, btn3)
        bot.send_photo(
            message.chat.id,
            file,
            caption=f"{list_of_users[user_number][1]}, {list_of_users[user_number][2]}, {list_of_users[user_number][6]} - {list_of_users[user_number][5]}",
            reply_markup=markup
        )

    
@bot.message_handler(func=lambda message: message.text in "Моя анкета")
def my_profile(message: telebot.types.Message) -> None:
    user_id = message.chat.id
    user_data = get_user(str(user_id))

    if user_data is not None:
        with open(f"{user_data[7]}", "rb") as file:
            bot.send_photo(
                message.chat.id,
                file,
                caption=f"{user_data[1]}, {user_data[2]}, {user_data[6]} - {user_data[5]}",
            )
    else:
        msg=bot.send_message(message.chat.id, "Введите свое имя")
        bot.register_next_step_handler(msg, process_username)
        

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton(USER_OPTIONS_YN[0])
    btn2 = KeyboardButton(USER_OPTIONS_YN[1])
    markup.row(btn1, btn2)
    msg = bot.send_message(
        message.chat.id, "Вот ваша анкета. Хотите оставить все как есть?", reply_markup=markup
    )
    bot.register_next_step_handler(message, redirect_user_to_start)


@bot.message_handler(func=lambda message: True)
def handle_all_start_messages(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    user_data_dict[user_id] = [user_id]
    if message.text in ["/start", "/hello"]:
        user_id = message.from_user.id
        user_data_dict[user_id] = [user_id]
        if get_user(str(user_id), get_user_info=False):
            user_data_dict[user_id] = [user_id]
            print(user_id)
            msg = bot.send_message(
            message.chat.id, "Здравствуй, я бот для поиска знакомств. Введите свое имя"
            )
            bot.register_next_step_handler(msg, process_username)
        else:
            bot.register_next_step_handler(message, user_options)
    else:
        if get_user(str(user_id), get_user_info=False):
            user_data_dict[user_id] = [user_id]
            print(user_id)
            msg = bot.send_message(
            message.chat.id, "Здравствуй, я бот для поиска знакомств. Введите свое имя"
            )
            bot.register_next_step_handler(msg, process_username)
        else:
            user_options
            msg = bot.send_message(message.chat.id, "Нет такого варианта ответа!")
    


if __name__ == "__main__":
    bot.polling(none_stop=True)

