from resourceDBManager import resourceDB, STATES_TABLE

class State:
    SLEEP = 0
    START = 1
    LEND = 2
    BORROW = 3
    LEND_USER_SELECTED = 4
    BORROW_USER_SELECTED = 5
    LEND_USER_NEW = 6
    BORROW_USER_NEW = 7
    LEND_WAIT_CONTACT = 8
    BORROW_WAIT_CONTACT = 9
    CLOSE = 10

class StatesResource:

    def setState(self, chatId, state, stateData = {}):
        table = resourceDB.Table(STATES_TABLE)
        item = {'chatId': chatId, 'state': state}
        item['data'] = {}
        for key in stateData:
            item['data'][key] = stateData[key]

        table.put_item(Item=item)

    def getItem(self, chatId):
        table = resourceDB.Table(STATES_TABLE)
        response = table.get_item(Key={'chatId': chatId})
        if 'Item' in response:
            return response['Item']

        return None

    def getStateFromItem(self, Item):
        if not Item:
            return -1

        if 'state' in Item:
            return Item['state']

        return -1

    def getDataFromItem(self, Item):
        if 'data' in Item:
            return Item['data']

        return None