import os
import telebot
from data_base_handler import save_to_db, get_user
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re
from dotenv import load_dotenv
import sqlite3

GENDER_OPTIONS = ["Девушка", "Парень", 'Не важно']
USER_OPTIONS_YN = ["Да", "Нет"]
DEFAULT_ERROR_TEMPLATES = {
    "common": "Произошла ошибка",
    "oneMoreTry": "попробуйте снова ввести",
}
MEDIA_FILE_PATH = ""
LIST_OF_USER_DATA = []
SET_OF_NUMBERS_STR = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "0"}

load_dotenv()
bot_token = os.environ["bot_token"]
bot = telebot.TeleBot(bot_token)


def process_username(message: telebot.types.Message) -> None:
    user_name = message.text
    if user_name:
        LIST_OF_USER_DATA.append(user_name)
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
    age = message.text
    if age and (set(age) <= SET_OF_NUMBERS_STR) and 14 < int(age) < 100:
        LIST_OF_USER_DATA.append(age)
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
    gender = message.text
    if gender == GENDER_OPTIONS[0] or gender == GENDER_OPTIONS[1]:
        LIST_OF_USER_DATA.append(gender)
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
    markup = ReplyKeyboardRemove()
    user_preferences = message.text
    if (
        user_preferences == GENDER_OPTIONS[0]
        or user_preferences == GENDER_OPTIONS[1]
        or user_preferences == GENDER_OPTIONS[2]
    ):
        LIST_OF_USER_DATA.append(user_preferences)
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
    user_info = message.text
    if user_info:
        LIST_OF_USER_DATA.append(user_info)
        place = bot.send_message(message.chat.id, text="Откуда вы?")
        bot.register_next_step_handler(place, process_place)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'{DEFAULT_ERROR_TEMPLATES["common"]}, {DEFAULT_ERROR_TEMPLATES["oneMoreTry"]} информацию о пользователе',
        )
        bot.register_next_step_handler(msg, process_user_info)


def process_place(message: telebot.types.Message) -> None:
    user_place = message.text
    if user_place and user_place == re.sub("[*#0-9]", "", user_place):
        LIST_OF_USER_DATA.append(user_place)
        msg = bot.send_message(message.chat.id, text="Отправьте свое фото")
        bot.register_next_step_handler(msg, process_image)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'{DEFAULT_ERROR_TEMPLATES["common"]}, {DEFAULT_ERROR_TEMPLATES["oneMoreTry"]} свое местоположение',
        )
        bot.register_next_step_handler(msg, process_place)


def process_image(message: telebot.types.Message) -> None:
    global MEDIA_FILE_PATH, LIST_OF_USER_DATA
    try:
        photo_file = bot.get_file(message.photo[-1].file_id)
        if photo_file:
            downloaded_file = bot.download_file(photo_file.file_path)

            MEDIA_FILE_PATH = f"images/{photo_file.file_id}.jpg"
            LIST_OF_USER_DATA.append(MEDIA_FILE_PATH)

            with open(MEDIA_FILE_PATH, "wb") as file:
                file.write(downloaded_file)

            with open(MEDIA_FILE_PATH, "rb") as file:
                bot.send_photo(
                    message.chat.id,
                    file,
                    caption=f"{LIST_OF_USER_DATA[1]}, {LIST_OF_USER_DATA[2]}, {LIST_OF_USER_DATA[6]} - {LIST_OF_USER_DATA[5]}",
                )

            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = KeyboardButton(USER_OPTIONS_YN[0])
            btn2 = KeyboardButton(USER_OPTIONS_YN[1])
            markup.row(btn1, btn2)
            reply = bot.send_message(
                message.chat.id, f"Вот ваша анкета, идем дальше?", reply_markup=markup
            )
            bot.register_next_step_handler(reply, redirect_user_to_start)

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
        LIST_OF_USER_DATA = LIST_OF_USER_DATA[:1]
        bot.register_next_step_handler(message, process_username)


def redirect_user_to_start(message: telebot.types.Message) -> None:
    global LIST_OF_USER_DATA
    reply = message.text
    if reply == USER_OPTIONS_YN[1]:
        LIST_OF_USER_DATA = LIST_OF_USER_DATA[:1]
        print(LIST_OF_USER_DATA)
        markup = ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, "Введите имя", reply_markup=markup)
        bot.register_next_step_handler(msg, process_username)
        os.remove(MEDIA_FILE_PATH)
    elif reply == USER_OPTIONS_YN[0]:
        save_to_db(LIST_OF_USER_DATA)
        bot.register_next_step_handler(message, user_options)
    else:
        msg = bot.send_message(
            message.chat.id,
            f'Выберите "{USER_OPTIONS_YN[0]}" или "{USER_OPTIONS_YN[1]}"',
        )
        bot.register_next_step_handler(msg, redirect_user_to_start)


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message: telebot.types.Message) -> None:
    user_id = message.from_user.id
    if get_user(str(user_id), get_user_info=False):
        LIST_OF_USER_DATA.append(user_id)
        print(user_id)
        msg = bot.send_message(
            message.chat.id, "Здравствуй, я бот для поиска знакомств. Введите свое имя"
        )
        bot.register_next_step_handler(msg, process_username)
    else:
        bot.register_next_step_handler(message, user_options)


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
    bot.register_next_step_handler(msg, redirect_func)


def redirect_func(message: telebot.types.Message) -> None:
    msg = message.text
    match msg:
        case "Начать поиск":
            bot.register_next_step_handler(message, search_for_match)
        case "Моя анкета":
            bot.register_next_step_handler(message, my_profile)
        case "Посмотреть кто меня лайкнул":
            pass
        case "Режим рандомной переписки":
            pass
        case "Не хочу никого искать":
            pass
        case "Отправить донат разработчикам:)":
            pass


def search_for_match(message: telebot.types.Message) -> None:
    pass


def my_profile(message: telebot.types.Message) -> None:
    user_id = message.chat.id
    user_data = get_user(str(user_id))

    with open(f"{user_data[7]}", "rb") as file:
        bot.send_photo(
            message.chat.id,
            file,
            caption=f"{user_data[1]}, {user_data[2]}, {user_data[6]} - {user_data[5]}",
        )
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton(USER_OPTIONS_YN[0])
    btn2 = KeyboardButton(USER_OPTIONS_YN[1])
    markup.row(btn1, btn2)
    msg = bot.send_message(
        message.chat.id, "Хотите изменить анкету?", reply_markup=markup
    )
    # Изменение анкеты


if __name__ == "__main__":
    bot.polling(none_stop=True)
