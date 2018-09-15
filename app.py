# app.py

import requests
import boto3
import os
import telebot
from flask import Flask, jsonify, request
from teleUpdates import CommandHandler, Dispatcher

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

def start(update):
    message = update["message"]
    app.logger.info('start from %i', message["from"]["id"])
    bot.send_message(message["from"]["id"], "start")

def text(update):
    message = update["message"]
    app.logger.info('text from %i', message["from"]["id"])
    bot.send_message(message["from"]["id"], message["text"])

startHandler = CommandHandler("start", start)
dispather.addHandler(startHandler)
dispather.setTextCallback(text)

@app.route("/{}".format(bot_token), methods=["POST"])
def bot_main():
    update = request.get_json()
    if "message" in update:
        dispather.processUpdate(update)
    return "ok!", 200


@app.route("/test", methods=["GET"])
def test():
    return jsonify({'test': "OK"})
