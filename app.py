# app.py

import requests
import os
import telebot
import pprint
import json
from flask import Flask, jsonify, request
from teleUpdates import MessageHandler, CallbackHandler, Dispatcher
from usersTableResource import UsersTableResource

bot_token = os.environ.get('DEBT_BOT_TOKEN')
app = Flask(__name__)

bot = telebot.TeleBot(bot_token)
dispather = Dispatcher()
utResource = UsersTableResource()

def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btnLend = telebot.types.InlineKeyboardButton('Lend')
    dataLend = {'Action' : 'Lend'};
    btnLend.callback_data = json.dumps(dataLend)
    btnBorrow = telebot.types.InlineKeyboardButton('Borrow')
    dataBorrow = {'Action': 'Borrow'};
    btnBorrow.callback_data = json.dumps(dataBorrow)
    markup.add(btnLend, btnBorrow)
    bot.send_message(message["from"]["id"], "Choose action:", reply_markup=markup)

def text(message):
    bot.send_message(message["from"]["id"], message["text"])

def onLend(callbackQuery):
    bot.answer_callback_query(callbackQuery["id"])
    Lend(callbackQuery["from"]["id"])

def Lend(chatID):
    bot.send_message(chatID, "Select user to lend money")
    return

def onBorrow(callbackQuery):
    bot.answer_callback_query(callbackQuery["id"])
    Borrow(callbackQuery["from"]["id"])

def Borrow(chatID):
    bot.send_message(chatID, "Select user to borrow money")
    return


startHandler = MessageHandler("start", start)
lendHandler = CallbackHandler("Action", "Lend", onLend)
borrowHandler = CallbackHandler("Action", "Borrow", onBorrow)
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
    utResource.mergeRecord(chatId, "Vasia", 200)
    utResource.mergeRecord(chatId, "Petia", 100)

    return jsonify({'testDB': "OK"})

@app.route("/all", methods=["GET"])
def all():
    chatId = 447198168
    item = utResource.getItem(chatId)
    return jsonify({' '.join(item['data'].keys()): "OK"})
