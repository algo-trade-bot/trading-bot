from kraken_wsclient_py import WssClient as client


ticker_ids={}
def my_handler(message):
    # Here you can do stuff with the messages
    global ticker_ids

    if(type(message) is dict and 'channelID' in message.keys() and 'pair' in message.keys()):
        ticker_ids[message['channelID']] = str(message['pair'])
        print(message['channelID'], message['pair'])
         
    elif (message.__class__ is list):
        ticker_id = message[0]
        temp = message[1]
        bid_list = temp.get('b')
        bid_price = bid_list[0]
        print(ticker_ids.get(ticker_id), bid_price)
        
    # print(message)

my_client = client()
my_client.start()

# Sample public-data subscription:

my_client.subscribe_public(
    subscription = {
        'name': 'ticker'
    },
    pair = ['XBT/USD', 'XRP/USD'],
    callback = my_handler
)
