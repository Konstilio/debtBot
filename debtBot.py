import telebot
from usersTableResource import User

class DebtBot(telebot.TeleBot):
    def __init__(self, token):
        super().__init__(token)

    def sendUserStatusMessage(self, chatId, user, num):

        if user.telegramId != 0:
            userName = "[{}](tg://user?id={})".format(user.userName,user.telegramId)
        else:
            userName = user.userName

        if num > 0:
            super().send_message(chatId, "%s owns you %0.2f" % (userName, num), parse_mode="markdown")
        elif num < 0:
            super().send_message(chatId, "You own %0.2f to %s" % (-num, userName), parse_mode="markdown")