from resourceDBManager import resourceDB, USERS_TABLE

class UsersTableResource:

    def mergeRecord(self, chatId, user, num):
        table = resourceDB.Table(USERS_TABLE)
        response = table.get_item(Key={'chatId': chatId})
        print(response)
        if 'Item' in response:
            item = response['Item']
            data = item['data']
            if user in data:
                data[user] += num
            else:
                data[user] = num
        else:
            item = {}
            item['chatId'] = chatId
            item['data'] = {user : num}

        table.put_item(Item = item)

    def getItem(self, chatId):
        table = resourceDB.Table(USERS_TABLE)
        response = table.get_item(Key={'chatId': chatId})
        return response['Item']