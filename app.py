# app.py

import requests
import boto3
import os
import telebot
import pprint
from flask import Flask, jsonify, request
from teleUpdates import MessageHandler, CallbackHandler, Dispatcher

USERS_TABLE = os.environ['USERS_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:5000'
    )
else:
    client = boto3.client('dynamodb')

app = Flask(__name__)

bot_token = "625324478:AAHwqiUfVvpo3MxrrBwSMb0kf-v56Q8rlnc"
bot = telebot.TeleBot(bot_token)
dispather = Dispatcher()

def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btnLend = telebot.types.InlineKeyboardButton('Lend')
    btnLend.callback_data = "Lend"
    btnBorrow = telebot.types.InlineKeyboardButton('Borrow')
    btnBorrow.callback_data = "Borrow"
    markup.add(btnLend, btnBorrow)
    bot.send_message(message["from"]["id"], "Choose action:", reply_markup=markup)

def text(message):
    bot.send_message(message["from"]["id"], message["text"])

def onLend(callbackQuery):
    bot.send_message(callbackQuery["from"]["id"], "Yes")

def onBorrow(callbackQuery):
    bot.send_message(callbackQuery["from"]["id"], "No")


startHandler = MessageHandler("start", start)
lendHandler = CallbackHandler("Lend", onLend)
borrowHandler = CallbackHandler("Borrow", onBorrow)
dispather.addMessageHandler(startHandler)
dispather.addCallbackHandler(lendHandler)
dispather.addCallbackHandler(borrowHandler)
dispather.setTextCallback(text)

@app.route("/{}".format(bot_token), methods=["POST"])
def bot_main():
    update = request.get_json()
    app.logger.info(update)
    dispather.processUpdate(update)
    return "ok!", 200


@app.route("/test", methods=["GET"])
def test():
    return jsonify({'test': "OK"})
