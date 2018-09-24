from resourceDBManager import resourceDB, USERS_TABLE

class User:
    def __init__(self, name, phone = None, telegramId = 0):
        self.userName = name
        self.phone = phone
        self.telegramId = telegramId

class UsersTableResource:

    def mergeRecord(self, chatId, user, num):
        table = resourceDB.Table(USERS_TABLE)
        response = table.get_item(Key={'chatId': chatId})
        print(response)
        if 'Item' in response:
            item = response['Item']
            data = item['data']
            if user.userName in data:
                data[user.userName]['num'] += num
            else:
                data[user.userName] = {'num' : num}
                if user.telegramId != 0:
                    data[user.userName]['phone'] = user.phone
                    data[user.userName]['telegramId'] = user.telegramId
        else:
            item = {}
            item['chatId'] = chatId
            item['data'] = {user.userName : {'num' : num}}
            if user.telegramId != 0:
                item['data'][user.userName]['phone'] = user.phone
                item['data'][user.userName]['telegramId'] = user.telegramId

        table.put_item(Item = item)

    def getItemData(self, chatId):
        table = resourceDB.Table(USERS_TABLE)
        response = table.get_item(Key={'chatId': chatId})

        if not 'Item' in response:
            return None

        item = response['Item']
        if not 'data' in item:
            return None

        return item['data']

    def getCurrentUsers(self, chatId):
        table = resourceDB.Table(USERS_TABLE)
        response = table.get_item(Key={'chatId': chatId})

        if not 'Item' in response:
            return []
        if not 'data' in response['Item']:
            return []

        return response['Item']['data'].keys()