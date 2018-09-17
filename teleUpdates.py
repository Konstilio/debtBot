import json

class MessageHandler:
    def __init__(self, command, callback):
        self.command = command.lower()
        self.callback = callback

class CallbackHandler:
    def __init__(self, key, data, callback):
        self.key = key
        self.data = data
        self.callback = callback

class Dispatcher:
    def __init__(self):
        self.messageHandlers = {}
        self.callbackHandlers = {}
        self.textCallback = None

    def addMessageHandler(self, handler):
        self.messageHandlers[handler.command] = handler

    def addCallbackHandler(self, handler):
        if handler.key in self.callbackHandlers:
            self.callbackHandlers[handler.key][handler.data] = handler
        else:
            self.callbackHandlers[handler.key] = {handler.data : handler}
        self.callbackHandlers[handler.data] = handler

    def setTextCallback(self, textCallback):
        self.textCallback = textCallback

    def processUpdate(self, update):
        if "message" in update:
            message = update["message"]
            text = message["text"]
            if text.startswith('/'):
                command = text[1:]
                if command in self.messageHandlers:
                    self.messageHandlers[command].callback(message)
            else:
                if self.textCallback:
                    self.textCallback(message)
        elif "callback_query" in update:
            callback_query = update["callback_query"]
            callback_data = callback_query["data"]
            dataJSON = json.loads(callback_data)
            for key in dataJSON.keys():
                if key in self.callbackHandlers:
                    handlerDict = self.callbackHandlers[key]
                    data = dataJSON[key]
                    if data in handlerDict:
                        handlerDict[data].callback(callback_query)

