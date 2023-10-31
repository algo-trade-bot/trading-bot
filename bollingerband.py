from trade_controller import TradeController
from kraken_wsclient_py import WssClient as WsClient
import pandas as pd


class BollingerBandTrade:

    def __init__(self, window_size):
        self.controller = TradeController()
        self.universe = self.controller.get_ticker_info(None)
        self.coarse = None
        self.fine = None
        self.channel_mapping = {}
        self.bands = None
        self.window_size = window_size

    def coarse_selection(self, criterion='v', sample_size=50):
        coarse = [(k, v) for k, v in self.universe['result'].items() if k[-3:] == 'USD']
        coarse.sort(key=lambda x: x[1][criterion][0], reverse=True)
        self.coarse = coarse[:sample_size]

    def fine_selection(self, criterion='t', sample_size=10):
        fine = self.coarse
        fine.sort(key=lambda x: x[1][criterion][0], reverse=True)
        self.fine = [pair for pair, info in fine][:sample_size]

    def prepare_execution(self):
        pair_info = self.controller.get_tradable_asset_pairs(self.fine)['result']
        self.fine = [val['wsname'] for _, val in pair_info.items()]

        self.bands = {pair: pd.DataFrame({
            'price': []
        }) for pair in self.fine}

    def update_bands(self, pair):
        self.bands[pair]['sma'] = self.bands[pair]['price'].rolling(window=self.window_size).mean()
        self.bands[pair]['std'] = self.bands[pair]['price'].rolling(window=self.window_size).std()
        self.bands[pair]['upper band'] = self.bands[pair]['sma'] + 2 * self.bands[pair]['std']
        self.bands[pair]['lower band'] = self.bands[pair]['sma'] + 2 * self.bands[pair]['std']

        if len(self.bands[pair]) > self.window_size:
            self.bands[pair] = self.bands[pair].tail(self.window_size)

    def execute_trade(self, pair):
        if self.bands[pair]['price']:
            if self.bands[pair]['price'] < self.bands[pair]['lower band']:
                # add buy command
                pass
            elif self.bands[pair]['price'] > self.bands[pair]['upper band']:
                # add sell command
                pass

    def websocket_handler(self, message):
        if isinstance(message, dict) and 'channelID' in message.keys() and 'pair' in message.keys():
            self.channel_mapping[message['channelID']] = str(message['pair'])

        elif isinstance(message, list):
            pair_name = self.channel_mapping[message[0]]
            last_price = message[1]['c'][0]
            print(pair_name, last_price)
            self.bands[pair_name] = pd.concat([self.bands[pair_name], pd.DataFrame({'price': [last_price]})],
                                              ignore_index=True)
            print(self.bands[pair_name])
            self.update_bands(pair_name)

    def websocket_start(self):
        my_client = WsClient()
        my_client.start()

        my_client.subscribe_public(
            subscription={
                'name': 'ticker'
            },
            pair=self.fine,
            callback=self.websocket_handler
        )

    def execute(self):
        self.coarse_selection()
        self.fine_selection()
        self.prepare_execution()
        self.websocket_start()
