# app.py
import os
import requests
import telebot
import pprint
import json
from decimal import Decimal
from flask import Flask, jsonify, request
from usersTableResource import UsersTableResource, User
from statesTableResource import StatesResource, State
from debtBot import DebtBot

bot_token = os.environ.get('DEBT_BOT_TOKEN')
app = Flask(__name__)

bot = DebtBot(bot_token)
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
    stateResource.setState(chatId, State.SLEEP)

@bot.message_handler(commands=['lend'])
def onLendCommand(message):
    Lend(message.chat.id)

@bot.message_handler(commands=['borrow'])
def onBorrowCommand(message):
    Borrow(message.chat.id)

@bot.message_handler(commands=['status'])
def Status(message):
    chatId = message.chat.id
    data = utResource.getItemData(chatId)

    if not data:
        bot.send_message(chatId, "You do not have any records")
    else:
        for key in data:
            user = utResource.getUserFromItemData(data, key)
            num = utResource.getNumFromItemData(data, key)
            bot.sendUserStatusMessage(chatId, user, num)

    stateResource.setState(chatId, State.SLEEP)

def setupUsersMarkup(chatID, actionName, actionNewName, actionContactName):
    users = utResource.getCurrentUsers(chatID)
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for user in users:
        btn = telebot.types.InlineKeyboardButton(user)
        btnData = {actionName: user};
        btn.callback_data = json.dumps(btnData)
        markup.add(btn)

    btnNew = telebot.types.InlineKeyboardButton('new record')
    btnNew.callback_data = actionNewName
    markup.add(btnNew)

    btnContact = telebot.types.InlineKeyboardButton('choose from contact')
    btnContact.callback_data = actionContactName
    markup.add(btnContact)

    return markup

@bot.callback_query_handler(func=lambda callbackQuery: callbackQuery.data == 'Lend')
def onLend(callbackQuery):
    bot.answer_callback_query(callbackQuery.id)
    Lend(callbackQuery.from_user.id)

def Lend(chatId):
    markup = setupUsersMarkup(chatId, "ActionLend", "ActionLendNew", "ActionLendContact")
    bot.send_message(chatId, "Select user to lend money:", reply_markup=markup)
    stateResource.setState(chatId, State.LEND)

@bot.callback_query_handler(func=lambda callbackQuery: callbackQuery.data == 'Borrow')
def onBorrow(callbackQuery):
    bot.answer_callback_query(callbackQuery.id)
    Borrow(callbackQuery.from_user.id)

def Borrow(chatId):
    markup = setupUsersMarkup(chatId, "ActionBorrow", "ActionBorrowNew", "ActionBorrowContact")
    bot.send_message(chatId, "Select user to borrow money from: ", reply_markup=markup)
    stateResource.setState(chatId, State.BORROW)

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

@bot.callback_query_handler(func=lambda callbackQuery: callbackQuery.data in ['ActionLendContact', 'ActionBorrowContact'])
def onChooseFromContact(callbackQuery):
    bot.answer_callback_query(callbackQuery.id, "Ok, I see")
    chatId = callbackQuery.from_user.id

    stateItem = stateResource.getItem(chatId)
    state = stateResource.getStateFromItem(stateItem)

    if callbackQuery.data == 'ActionLendContact':
        if state != State.LEND:
            bot.send_message(chatId, "Oops, try again")
            stateResource.setState(chatId, State.SLEEP)
            return

        bot.send_message(chatId, "Please send me a contact you want to lend money to")
        stateResource.setState(chatId, State.LEND_WAIT_CONTACT)
    elif callbackQuery.data == 'ActionBorrowContact':
        if state != State.BORROW:
            bot.send_message(chatId, "Oops, try again")
            stateResource.setState(chatId, State.SLEEP)
            return

        bot.send_message(chatId, "Please send me a contact you want to borrow money from")
        stateResource.setState(chatId, State.BORROW_WAIT_CONTACT)


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

@bot.message_handler(content_types=['text'])
def text(message):
    chatId = message.chat.id
    try:
        text = message.text
        stateItem = stateResource.getItem(chatId)
        state = stateResource.getStateFromItem(stateItem)

        if state in [State.LEND_USER_NEW, State.BORROW_USER_NEW]:
            user = User(text)
            utResource.mergeRecord(chatId, user, 0)
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
            user = User(userName)
            if state == State.LEND_USER_SELECTED:
                utResource.mergeRecord(chatId, user, num)
                bot.send_message(chatId, "Your lend operation is saved")
            elif state == State.BORROW_USER_SELECTED:
                utResource.mergeRecord(chatId, user, -num)
                bot.send_message(chatId, "Your borrow operation is saved")
            stateResource.setState(chatId, State.SLEEP)
        else:
            raise Exception("Wrong state")
    except Exception as e:
        #TODO: show help
        app.logger.info("Exception: " + str(e))
        bot.send_message(chatId, "I do not understand you")
        stateResource.setState(chatId, State.SLEEP)

@bot.message_handler(content_types=['contact'])
def contact(message):
    chatId = message.chat.id
    contact = message.contact
    stateItem = stateResource.getItem(chatId)
    state = stateResource.getStateFromItem(stateItem)

    if state != State.LEND_WAIT_CONTACT and state != State.BORROW_WAIT_CONTACT:
        # TODO: show help
        bot.send_message(chatId, "Sorry, I do not understand you")
        stateResource.setState(chatId, State.SLEEP)
        return

    userName = ""
    if contact.first_name:
        userName += contact.first_name
    if contact.first_name and contact.last_name:
        userName += " "
    if contact.last_name:
        userName += contact.last_name
    user = User(userName, contact.phone_number, contact.user_id)
    utResource.mergeRecord(chatId, user, 0)

    if state == State.LEND_WAIT_CONTACT:
        bot.send_message(chatId, "How much do you want to lend to %s ?" % userName)
        stateResource.setState(chatId, State.LEND_USER_SELECTED, {"userName": userName})
    elif state == State.BORROW_WAIT_CONTACT:
        bot.send_message(chatId, "How much do you want to borrow from %s ?" % userName)
        stateResource.setState(chatId, State.BORROW_USER_SELECTED, {"userName": userName})


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
