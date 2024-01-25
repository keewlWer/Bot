def process_image(message):
    try:
        photo_file = bot.get_file(message.photo[-1].file_id)  # Получение самой большой версии фото
        downloaded_file = bot.download_file(photo_file.file_path)  # Загрузка файла

        local_file_path = f'images/{photo_file.file_id}.jpg'
        with open(local_file_path, 'wb') as file:
            file.write(downloaded_file)

        # Переоткрыть файл в режиме чтения для отправки
        with open(local_file_path, 'rb') as file:
            bot.send_photo(message.chat.id, file, caption=f'{list_of_user_data[0]}, {list_of_user_data[1]}, {list_of_user_data[5]} - {list_of_user_data[4]}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {type(e).__name__}, {e}')