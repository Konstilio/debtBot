# app.py

import requests
import os
import telebot
import pprint
import json
from decimal import Decimal
from flask import Flask, jsonify, request
from usersTableResource import UsersTableResource
from statesTableResource import StatesResource, State

bot_token = os.environ.get('DEBT_BOT_TOKEN')
app = Flask(__name__)

bot = telebot.TeleBot(bot_token)
utResource = UsersTableResource()
stateResource = StatesResource()

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btnLend = telebot.types.InlineKeyboardButton('Lend')
    btnLend.callback_data = 'Lend'
    btnBorrow = telebot.types.InlineKeyboardButton('Borrow')
    btnBorrow.callback_data = 'Borrow'
    markup.add(btnLend, btnBorrow)

    chatId = message.chat.id
    bot.send_message(chatId, "Choose action:", reply_markup=markup)
    stateResource.setState(chatId, State.SLEEP, {"userName": userName})

def setupUsersMarkup(chatID, actionName, actionNewName):
    users = utResource.getCurrentUsers(chatID)
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for user in users:
        btn = telebot.types.InlineKeyboardButton(user)
        btnData = {actionName: user};
        btn.callback_data = json.dumps(btnData)
        markup.add(btn)

    btnNew = telebot.types.InlineKeyboardButton('new')
    btnNew.callback_data = actionNewName
    markup.add(btnNew)
    return markup

@bot.callback_query_handler(func=lambda callbackQuery: callbackQuery.data == 'Lend')
def onLend(callbackQuery):
    bot.answer_callback_query(callbackQuery.id)
    Lend(callbackQuery.from_user.id)

def Lend(chatId):
    markup = setupUsersMarkup(chatId, "ActionLend", "ActionLendNew")
    bot.send_message(chatId, "Select user to lend money:", reply_markup=markup)
    stateResource.setState(chatId, State.LEND)

@bot.callback_query_handler(func=lambda callbackQuery: callbackQuery.data == 'Borrow')
def onBorrow(callbackQuery):
    bot.answer_callback_query(callbackQuery.id)
    Borrow(callbackQuery.from_user.id)

def Borrow(chatId):
    markup = setupUsersMarkup(chatId, "ActionBorrow", "ActionBorrowNew")
    bot.send_message(chatId, "Select user to borrow money from: ", reply_markup=markup)
    stateResource.setState(chatId, State.BORROW)

@bot.callback_query_handler(func=lambda callbackQuery: 'ActionLend' in json.loads(callbackQuery.data))
def onLendUserSelected(callbackQuery):
    bot.answer_callback_query(callbackQuery.id, "I got it")

    chatId = callbackQuery.from_user.id
    stateItem = stateResource.getItem(chatId)
    state = stateResource.getStateFromItem(stateItem)

    if state != State.LEND:
        bot.send_message(chatId, "Oops, try again")
        stateResource.setState(chatId, State.SLEEP)
        return

    data = json.loads(callbackQuery.data)
    userName = data['ActionLend']

    bot.send_message(chatId, "How much do you want to lend to %s ?" % userName)
    stateResource.setState(chatId, State.LEND_USER_SELECTED, {"userName" : userName})

@bot.callback_query_handler(func=lambda callbackQuery: 'ActionBorrow' in json.loads(callbackQuery.data))
def onBorrowUserSelected(callbackQuery):
    bot.answer_callback_query(callbackQuery.id, "I got it")

    chatId = callbackQuery.from_user.id
    stateItem = stateResource.getItem(chatId)
    state = stateResource.getStateFromItem(stateItem)

    if state != State.BORROW:
        bot.send_message(chatId, "Oops, try again")
        stateResource.setState(chatId, State.SLEEP)
        return

    data = json.loads(callbackQuery.data)
    userName = data['ActionBorrow']

    bot.send_message(chatId, "How much do you want to borrow from %s ?" % userName)
    stateResource.setState(chatId, State.BORROW_USER_SELECTED, {"userName": userName})

@bot.callback_query_handler(func=lambda callbackQuery: callbackQuery.data in ['ActionLendNew', 'ActionBorrowNew'])
def onCreateNewUser(callbackQuery):
    bot.answer_callback_query(callbackQuery.id)
    chatId = callbackQuery.from_user.id
    bot.send_message(chatId, "Enter new user name:")

    stateItem = stateResource.getItem(chatId)
    state = stateResource.getStateFromItem(stateItem)

    if callbackQuery.data == 'ActionLendNew':
        if state != State.LEND:
            bot.send_message(chatId, "Oops, try again")
            stateResource.setState(chatId, State.SLEEP)
            return

        stateResource.setState(chatId, State.LEND_USER_NEW)
    elif callbackQuery.data == 'ActionBorrowNew':
        if state != State.BORROW:
            bot.send_message(chatId, "Oops, try again")
            stateResource.setState(chatId, State.SLEEP)
            return

        stateResource.setState(chatId, State.BORROW_USER_NEW)


@bot.message_handler(content_types=['text'])
def text(message):
    chatId = message.chat.id
    try:
        text = message.text
        stateItem = stateResource.getItem(chatId)
        state = stateResource.getStateFromItem(stateItem)

        if state in [State.LEND_USER_NEW, State.BORROW_USER_NEW]:
            utResource.mergeRecord(chatId, text, 0)
            if state == State.LEND_USER_NEW:
                bot.send_message(chatId, "How much do you want to lend to %s ?" % text)
                stateResource.setState(chatId, State.LEND_USER_SELECTED, {"userName" : text})
            elif state == State.BORROW_USER_NEW:
                bot.send_message(chatId, "How much do you want to borrow from %s ?" % text)
                stateResource.setState(chatId, State.BORROW_USER_SELECTED, {"userName": text})
            return
        elif state in [State.LEND_USER_SELECTED, State.BORROW_USER_SELECTED]:
            num = Decimal(text)
            data = stateResource.getDataFromItem(stateItem)
            userName = data["userName"]
            if state == State.LEND_USER_SELECTED:
                utResource.mergeRecord(chatId, userName, num)
                bot.send_message(chatId, "Your lend operation is saved")
            elif state == State.BORROW_USER_SELECTED:
                utResource.mergeRecord(chatId, userName, -num)
                bot.send_message(chatId, "Your borrow operation is saved")
            stateResource.setState(chatId, State.SLEEP)
        else:
            raise Exception("Wrong state")
    except Exception as e:
        #TODO: show help
        app.logger.info("Exception: " + str(e))
        bot.send_message(chatId, "I do not understand you")
        stateResource.setState(chatId, State.SLEEP)




@app.route("/{}".format(bot_token), methods=["POST"])
def bot_main():
    update = request.get_json()
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    app.logger.info(update)
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
