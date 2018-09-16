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
bot_token = os.environ.get('DEBT_BOT_TOKEN')

if IS_OFFLINE:
    resourceDB = boto3.resource(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    resourceDB = boto3.resource('dynamodb')

app = Flask(__name__)

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
    bot.answer_callback_query(callbackQuery["id"])

def onBorrow(callbackQuery):
    bot.answer_callback_query(callbackQuery["id"])


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
    app.logger.info("token = " + bot_token)
    return jsonify({'test': "OK"})

@app.route("/testDB", methods=["GET"])
def testDB():
    chatId = 447198168
    table = resourceDB.Table(USERS_TABLE)

    item = {}
    item['chatId'] = chatId
    item['data'] = {'Vasia': 200, 'Petia': 100}

    table.put_item(Item=item)

    return jsonify({'testDB': "OK"})

@app.route("/all", methods=["GET"])
def all():
    chatId = 447198168
    table = resourceDB.Table(USERS_TABLE)
    response = table.get_item(Key={'chatId':chatId})
    print(response['Item'])
    return jsonify({'all': "OK"})
