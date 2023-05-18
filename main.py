import telebot
from telebot import types
import random
import os
import face_recognition
from PIL import Image, ImageDraw
import rembg
from model_torch_function import detect_xray
import psycopg2

#токен для бота, берется из Телеграма: BotFather
bot = telebot.TeleBot('6059040908:AAHG6F_f5BtpDa_bBrMyrYN6wqnxvf4LW3Y')

#получение фотки от пользователя и отправка в ответ пользователю фотки с распознанными лицами:
@bot.message_handler(content_types = ['photo'])
def get_photo(message):
    replies = ['Красивое фото!👍', "Отличное фото!🚀"] 
    bot.reply_to(message, random.choice(replies))

    raw = message.photo[2].file_id
    path = raw + '.jpg'
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # БЛОК С РАСПОЗНАВАНИЕМ ЛИЦ:
    img = face_recognition.load_image_file(path)
    img_location = face_recognition.face_locations(img)

    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)

    for (top, right, botton, left) in img_location:
        draw.rectangle(((left, top), (right, botton)),
                        outline = (15, 255, 0), width = 5)

    #Определяем количество лиц на фото и пишем пользователю, сколько лиц нашел бот:
    face_amount = len(img_location)
    #Задаем ответ бота о том, сколько лиц он нашел:
    if face_amount in [0, None]:
        bot.send_message(message.chat.id, 'Я не нашел лиц на твоем фото..☹')
    else:
        bot.send_photo(message.chat.id, pil_img)
        if (face_amount == 1 or face_amount % 10 == 1) and (face_amount != 11):
            bot.send_message(message.chat.id, f'Я нашел {len(img_location)} лицо на твоем фото 🙂')
        if face_amount in [2, 3, 4] or (face_amount % 10 in [2, 3, 4]):
            bot.send_message(message.chat.id, f'Я нашел {len(img_location)} лица на твоем фото 🙂')
        if face_amount in [5,6,7,8,9,11] or (face_amount % 10 in [5,6,7,8,9]):
            bot.send_message(message.chat.id, f'Я нашел {len(img_location)} лиц на твоем фото 🙂')
    del pil_img
    del draw
    os.remove(path) # Удаляем исходное изображение
    #os.remove('face_rec_result.jpg') # Удаляем обработанное изображение



#Команда Start (Справка по боту):
@bot.message_handler(commands = ['start'])
def send_greet(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nОтправь мне фото для распознавания или выбери другую опцию:')
    
    with open('description.txt', encoding = 'utf-8', mode = 'r') as f:
        bot.send_message(message.chat.id, f.read())

# Команда background (Удаление фона на изображении):
@bot.message_handler(commands = ['background'])
def get_photo(message):
    try:
        sent = bot.send_message(message.chat.id, 'Отправь мне фото для удаления фона')
        bot.register_next_step_handler(sent, remove_bg) #ПОШАГОВЫЙ ОБРАБОТЧИК
    except:
        sent = bot.send_message(message.chat.id, 'Неверные данные. Нажми /background и отправь фото еще раз')

def remove_bg(message): 
    try:
        raw = message.photo[2].file_id
        path = raw + '.jpg'
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(path, 'wb') as new_file:
            new_file.write(downloaded_file)

        open_image = Image.open(path)
        output = rembg.remove(open_image)
        bot.send_photo(message.chat.id, output)
        bot.send_message(message.chat.id, 'Готово)')
        del open_image
        del output
        os.remove(path)
    except:
        bot.send_message(message.chat.id, 'Неверные данные. Нажми /background и отправь фото еще раз')

#Команда xray (Определение вероятности пневмонии на рентген снимках)
@bot.message_handler(commands = ['xray'])
def get_photo(message):
    try:
        with open('disclaimer.txt', encoding = 'utf-8', mode = 'r') as f:
            bot.send_message(message.chat.id, f.read())
        sent = bot.send_message(message.chat.id, 'Отправь мне фото рентген-снимка грудной клетки')
        bot.register_next_step_handler(sent, detect_pneumonia) #ПОШАГОВЫЙ ОБРАБОТЧИК
    except:
        sent = bot.send_message(message.chat.id, 'Неверные данные. Нажми /xray и отправь снимок еще раз')

def detect_pneumonia(message):
    try:
        raw = message.photo[2].file_id
        path = raw + '.jpg'
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(path, 'wb') as new_file:
            new_file.write(downloaded_file)
        open_image = Image.open(path)
        prediction = detect_xray(path)
        
        if prediction == 1:
            bot.send_message(message.chat.id, 'На снимке вероятны очаги пневмонии')
        elif prediction == 0:
            bot.send_message(message.chat.id, 'Можно утверждать, что видимых очагов пневмонии на снимке не обнаружено')
        del open_image
        del prediction
        del downloaded_file
        os.remove(path)

    except:
        bot.send_message(message.chat.id, 'Нажми /xray и отправь снимок')
    
#Команда Game:
@bot.message_handler(commands = ['game'])
def play(message):
    games = ['🎲', '🎯', '🏀', '⚽', '🎳', '🎰']
    bot.send_message(message.chat.id, 'Сыграем?📱')
    game = random.choice(games)
    bot.send_dice(message.chat.id, game)
    
#Команда feedback:
@bot.message_handler(commands = ['feedback'])
def feedback(message):
    sent = bot.send_message(message.chat.id, 'Оставь отзыв о работе бота:🙂📱')
    bot.register_next_step_handler(sent, feedback)
def feedback(message):
    review_text = message.text
    with open('reviews.txt', encoding = 'utf-8',  mode = 'a') as f:
        f.write(review_text + ' - ' + message.from_user.first_name + '\n')
    if message.text is not None:
        bot.send_message(message.chat.id, 'Спасибо за отзыв)')

# Перейти на мою страницу на ГитХабе
@bot.message_handler(commands = ['site']) 
def site(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Перейти в профиль на GitHub',
                                          url = 'https://github.com/Kuaranir'))
    bot.reply_to(message, 'Мой профиль на GitHub', reply_markup = markup)

#Команда survey:
@bot.message_handler(commands = ['survey'])
def survey(message):
    sent = bot.send_message(message.chat.id, 'Пройди опрос из пары вопросов.\nВведи через запятую возраст, город и любимую музыкальную группу🎸')
    bot.register_next_step_handler(sent, survey)

def survey(message):
    answer = message.text
    data = answer.split(',')
    age, city, band = data[0], data[1], data[2]

    connection = psycopg2.connect(user = 'postgres',
                                  password = '23q56q89',
                                  host = '127.0.0.1',
                                  port = '5432',
                                  database = 'mytelegram')
    cursor = connection.cursor()
    postgres_insert_query = 'INSERT INTO bands (age, city, band) VALUES (%s, %s, %s)'
    values_to_insert = (age, city, band)
    cursor.execute(postgres_insert_query, values_to_insert)
    connection.commit()

    bot.send_message(message.chat.id, 'Спасибо🙂')


#Если юзер пишет боту "Привет":
@bot.message_handler()
def info(message):
    if message.text.lower() in 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')
    elif message.text.lower() in 'как дела':
        bot.send_message(message.chat.id, f'Хорошо, а у тебя?')
    else:
        bot.send_message(message.chat.id, 'Выбери нужное действие из списка команд /start')
        
#чтобы программа для бота выполнялась непрерывно, нужно прописать:
bot.polling(non_stop = True)
