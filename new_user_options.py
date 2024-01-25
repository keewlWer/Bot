import os
import telebot
from data_base_handler import save_to_db
from telebot.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
import re

USER_EXISTS = None
PREFERENCE_OPTIONS = ["Девушек", "Парней", "Не важно"]
GENDER_OPTIONS = ["Девушка", "Парень"]
USER_OPTIONS_YN = ["Да", "Нет"]
DEFAULT_ERROR_TEMPLATE = ['Произошла ошибка', 'попробуйте снова ввести']
BOT_TOKEN = "6738750456:AAEq0h_CefED8tEPGMxmPtwr93PNsG99wAs"

list_of_user_data = []
bot = telebot.TeleBot(BOT_TOKEN)
MEDIA_FILE_PATH = ''
set_of_numbers = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "0"}


def process_username(message):
    user_name = message.text
    if user_name:
        list_of_user_data.append(user_name)
        msg = bot.send_message(message.chat.id, f'{user_name.capitalize()}, введите свой возраст')
        bot.register_next_step_handler(msg, process_age)
    else:
        msg = bot.send_message(message.chat.id, f'{DEFAULT_ERROR_TEMPLATE}, введите имя еще раз')
        bot.register_next_step_handler(msg, process_username)


def process_age(message):
    age = message.text
    if age and (set(age) <= set_of_numbers):
        list_of_user_data.append(age)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = KeyboardButton(GENDER_OPTIONS[0])
        btn2 = KeyboardButton(GENDER_OPTIONS[1])
        markup.row(btn1, btn2)
        msg = bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_gender)
    else:
        msg = bot.send_message(message.chat.id, f'{DEFAULT_ERROR_TEMPLATE[0]}, {DEFAULT_ERROR_TEMPLATE[1]} возраст')
        bot.register_next_step_handler(msg, process_age)


def process_gender(message):
    gender = message.text
    if gender == GENDER_OPTIONS[0] or gender == GENDER_OPTIONS[1]:
        list_of_user_data.append(gender)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = KeyboardButton(PREFERENCE_OPTIONS[0])
        btn2 = KeyboardButton(PREFERENCE_OPTIONS[1])
        btn3 = KeyboardButton(PREFERENCE_OPTIONS[2])
        markup.row(btn1, btn2, btn3)
        msg = bot.send_message(message.chat.id, "Кого вы хотите найти?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_preferences)
    else:
        msg = bot.send_message(message.chat.id, f'{DEFAULT_ERROR_TEMPLATE[0]}, {DEFAULT_ERROR_TEMPLATE[1]} свой пол')
        bot.register_next_step_handler(msg, process_gender)


def process_preferences(message):
    markup = ReplyKeyboardRemove()
    user_preferences = message.text
    if user_preferences == PREFERENCE_OPTIONS[0] or user_preferences == PREFERENCE_OPTIONS[1] or user_preferences == PREFERENCE_OPTIONS[2]:
        list_of_user_data.append(user_preferences)
        info = bot.send_message(message.chat.id, text='Напишите что-нибудь о себе', reply_markup=markup)
        bot.register_next_step_handler(info, process_user_info)
    else:
        msg = bot.send_message(message.chat.id, f'{DEFAULT_ERROR_TEMPLATE[0]}, {DEFAULT_ERROR_TEMPLATE[1]} свои предпочтения')
        bot.register_next_step_handler(msg, process_preferences)


def process_user_info(message):
    user_info = message.text
    if user_info:
        list_of_user_data.append(user_info)
        place = bot.send_message(message.chat.id, text='Откуда вы?')
        bot.register_next_step_handler(place, process_place)
    else:
        msg = bot.send_message(message.chat.id, f'{DEFAULT_ERROR_TEMPLATE[0]}, {DEFAULT_ERROR_TEMPLATE[1]} информацию о пользователе')
        bot.register_next_step_handler(msg, process_user_info)


def process_place(message):
    user_place = message.text
    if user_place and user_place == re.sub('[*#0-9]', '', user_place):
        list_of_user_data.append(user_place)
        msg = bot.send_message(message.chat.id, text='Отправьте свое фото')
        bot.register_next_step_handler(msg, process_image)
    else:
        msg = bot.send_message(message.chat.id, f'{DEFAULT_ERROR_TEMPLATE[0]}, {DEFAULT_ERROR_TEMPLATE[1]} свое местоположение')
        bot.register_next_step_handler(msg, process_place)


def process_image(message):
    global MEDIA_FILE_PATH, list_of_user_data
    try:
        photo_file = bot.get_file(message.photo[-1].file_id)
        if photo_file:
            downloaded_file = bot.download_file(photo_file.file_path)

            MEDIA_FILE_PATH = f'images/{photo_file.file_id}.jpg'
            list_of_user_data.append(MEDIA_FILE_PATH)

            with open(MEDIA_FILE_PATH, 'wb') as file:
                file.write(downloaded_file)

            with open(MEDIA_FILE_PATH, 'rb') as file:
                bot.send_photo(message.chat.id, file, caption=f'{list_of_user_data[1]}, {list_of_user_data[2]}, {list_of_user_data[6]} - {list_of_user_data[5]}')

            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = KeyboardButton(USER_OPTIONS_YN[0])
            btn2 = KeyboardButton(USER_OPTIONS_YN[1])
            markup.row(btn1, btn2)
            reply = bot.send_message(message.chat.id, f'Вот ваша анкета, идем дальше?', reply_markup=markup)
            bot.register_next_step_handler(reply, redirect_user_to_start)

        else:
            msg = bot.send_message(message.chat.id, f'{DEFAULT_ERROR_TEMPLATE[0]} при обработке фото, попробуйте отправить фото еще раз')
            bot.register_next_step_handler(msg, process_image)

    except Exception as e:
        bot.send_message(message.chat.id, f'{DEFAULT_ERROR_TEMPLATE[0]}: {type(e).__name__}, {e}')
        list_of_user_data = list_of_user_data[:1]
        bot.register_next_step_handler(message, process_username)


def redirect_user_to_start(message):
    global list_of_user_data
    reply = message.text
    if reply == USER_OPTIONS_YN[0]:
        list_of_user_data = list_of_user_data[:1]
        print(list_of_user_data)
        markup = ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, "Введи имя", reply_markup=markup)
        bot.register_next_step_handler(msg, process_username)
        os.remove(MEDIA_FILE_PATH)
    elif reply == USER_OPTIONS_YN[1]:
        save_to_db(list_of_user_data)
        # next step
    else:
        msg = bot.send_message(message.chat.id, f'Выберите "{USER_OPTIONS_YN[0]}" или "{USER_OPTIONS_YN[1]}"')
        bot.register_next_step_handler(msg, redirect_user_to_start)


if not USER_EXISTS:
    @bot.message_handler(commands=['start', 'hello'])
    def send_welcome(message):
        user_id = message.from_user.id
        list_of_user_data.append(user_id)
        print(user_id)
        msg = bot.send_message(message.chat.id, "Здравствуй, я бот для поиска знакомств. Введи свое имя")
        bot.register_next_step_handler(msg, process_username)

bot.polling(none_stop=True)
