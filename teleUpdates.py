class CommandHandler:
    def __init__(self, command, callback):
        self.command = command.lower()
        self.callback = callback

class Dispatcher:
    def __init__(self):
        self.handlers = {}
        self.textCallback = None

    def addHandler(self, handler):
        self.handlers[handler.command] = handler

    def setTextCallback(self, textCallback):
        self.textCallback = textCallback

    def processUpdate(self, update):
        message = update["message"]
        text = message["text"]
        if text.startswith('/'):
            command = text[1:]
            if command in self.handlers:
                self.handlers[command].callback(update)
        else:
            if self.textCallback:
                self.textCallback(update)