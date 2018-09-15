# app.py

import requests
import boto3
import os
import telebot
from flask import Flask, jsonify, request

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

def process_update(update):
    message = update["message"]
    if "from" in message:
        if message["text"] == '/start':
            app.logger.info('process_update send start options to %i', message["from"]["id"])
            bot.send_message(message["from"]["id"], "start")
        else:
            bot.send_message(message["from"]["id"], "I can hear you")

@app.route("/{}".format(bot_token), methods=["POST"])
def bot_main():
    update = request.get_json()
    if "message" in update:
        process_update(update)
    return "ok!", 200


@app.route("/test", methods=["GET"])
def test():
    return jsonify({'test': "OK"})
