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

    def closeRecord(self, chatId, user):
        table = resourceDB.Table(USERS_TABLE)
        response = table.get_item(Key={'chatId': chatId})
        if not 'Item' in response:
            return

        item = response['Item']
        data = item['data']

        if not user.userName in data:
            return

        data[user.userName]['num'] = 0
        table.put_item(Item=item)


    def getItemData(self, chatId):
        table = resourceDB.Table(USERS_TABLE)
        response = table.get_item(Key={'chatId': chatId})

        if not 'Item' in response:
            return None

        item = response['Item']
        if not 'data' in item:
            return None

        return item['data']

    def getUserFromItemData(self, itemData, userName):
        if userName not in itemData:
            return None

        userData = itemData[userName]

        phone = userData['phone'] if 'phone' in userData else None
        telegramId = userData['telegramId'] if 'telegramId' in userData else 0
        return User(userName, phone, telegramId)

    def getNumFromItemData(self, itemData, userName):
        if userName not in itemData:
            return 0

        userData = itemData[userName]
        return userData['num']

    def getCurrentUsers(self, chatId):
        table = resourceDB.Table(USERS_TABLE)
        response = table.get_item(Key={'chatId': chatId})

        if not 'Item' in response:
            return []
        if not 'data' in response['Item']:
            return []

        return response['Item']['data'].keys()