from telegram.ext import Updater
from telegram.ext import CommandHandler
import cv2
import os
from datetime import datetime

TOKEN = ""
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def create_image(chat_id):
    image = cv2.imread(r"manul.jpg")

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 2
    color = (0, 0, 255)
    thickness = 3

    now = datetime.now()
    text = now.strftime("%d.%m.%Y %H-%M")
    textsize = cv2.getTextSize(text, font, fontScale, thickness)[0]
    textX = int((image.shape[1] - textsize[0]) / 2)
    textY = int((image.shape[0] + textsize[1]) / 2)

    # add text centered on image
    image = cv2.putText(image, text, (textX, textY), font, fontScale, color, thickness)
    image_bytes = cv2.imencode('.jpg', image)[1].tobytes()
    return image_bytes


def start(update, context):
    chat_id = update.effective_chat.id
    image = create_image(chat_id)
    context.bot.send_photo(chat_id=chat_id, photo=image)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()




