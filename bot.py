import telebot
import tensorflow as tf
from tensorflow.keras.models import load_model
import keras
import cv2
import skimage.transform
import re
import json
import decorator
import os
from flask import Flask, request

api_key = "1045675720:AAGV3UhR4Ks4mkV-x1ZTfjF8et0Iudp3hbk"

bot = telebot.TeleBot(api_key)

server = Flask(__name__)

@decorator.decorator
def errLog(func, *args, **kwargs):
    result = None
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        print(e.__repr__())
    return result


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, ты написал мне /start А теперь пришли мне boxid футболиста, а я попробую угадать его label.')

@errLog
def processPhotoMessage(message):
    print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    file = bot.get_file(fileID)
    print('file.file_path =', file.file_path)
    downloaded_file = bot.download_file(file.file_path)
    # downloaded_file = cv2.fromarray(downloaded_file)
    # img = cv2.imdecode(downloaded_file, 1)
    with open("image.png", 'wb') as new_file:
        new_file.write(downloaded_file)
    img = cv2.imread("image.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = skimage.transform.resize(img, (83, 45))
    img = img.reshape(1, img.shape[0], img.shape[1], img.shape[2])
    label = model.predict_classes(img)[0]
    bot.send_message(message.chat.id, str(label))
    print(f"Label {label} was sended!")
    
@bot.message_handler(content_types=['photo'])
def photo(message):
    processPhotoMessage(message)

@server.route('/' + api_key, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://stormy-brook-78919.herokuapp.com/' + api_key)
    return "!", 200

if __name__ == '__main__':
    model = load_model("model_100.h5")
    print("it's started")
    server.debug = True
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
#bot.polling()