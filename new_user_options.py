import os
import telebot
from data_base_handler import save_to_db
from telebot.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
from PIL import Image
from io import BytesIO

USER_EXISTS = None
list_of_user_data = []
BOT_TOKEN = "6738750456:AAEq0h_CefED8tEPGMxmPtwr93PNsG99wAs"
bot = telebot.TeleBot(BOT_TOKEN)


def process_username(message):
    user_name = message.text
    list_of_user_data.append(user_name)
    msg = bot.send_message(message.chat.id, f'{user_name.capitalize()}, введите свой возраст')
    bot.register_next_step_handler(msg, process_age)


def process_age(message):
    age = message.text
    list_of_user_data.append(age)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("Девушка")
    btn2 = KeyboardButton("Парень")
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_gender)


def process_gender(message):
    gender = message.text
    list_of_user_data.append(gender)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("Девушек")
    btn2 = KeyboardButton("Парней")
    btn3 = KeyboardButton('Не важно')
    markup.row(btn1, btn2, btn3)
    msg = bot.send_message(message.chat.id, "Кого вы хотите найти?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_preferences)


def process_preferences(message):
    markup = ReplyKeyboardRemove()
    user_preferences = message.text
    list_of_user_data.append(user_preferences)
    info = bot.send_message(message.chat.id, text='Напишите что-нибудь о себе', reply_markup=markup)
    bot.register_next_step_handler(info, process_user_info)


def process_user_info(message):
    user_info = message.text
    list_of_user_data.append(user_info)
    place = bot.send_message(message.chat.id, text='Откуда вы?')
    bot.register_next_step_handler(place, process_place)


def process_place(message):
    user_place = message.text
    list_of_user_data.append(user_place)
    msg = bot.send_message(message.chat.id, text='Отправьте свое фото')
    bot.register_next_step_handler(msg, process_image)


def process_image(message):
    file_info = bot.get_file(message.photo[1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image = Image.open(BytesIO(downloaded_file))
    image.save('image.jpg')
    save_to_db(list_of_user_data)
    with open('image.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f'{list_of_user_data[0]},{list_of_user_data[1]}, {list_of_user_data[5]} - {list_of_user_data[4]}')



if not USER_EXISTS:
    @bot.message_handler(commands=['start', 'hello'])
    def send_welcome(message):
        msg = bot.send_message(message.chat.id, "Здравствуй, я бот Субару. Введи имя")
        bot.register_next_step_handler(msg, process_username)

bot.polling(none_stop=True)