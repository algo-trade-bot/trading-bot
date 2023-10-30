from trade_controller import TradeController

class BollingerBandTrade:

    def __init__(self):
        self.controller = TradeController()
        self.universe = self.controller.get_ticker_info(None)
        self.coarse = None
        self.fine = None

    def coarse_selection(self, criterion='v', sample_size=50):
        coarse = [(k, v) for k, v in self.universe['result'].items() if k[-3:] == 'USD']
        coarse.sort(key=lambda x: x[1][criterion][0], reverse=True)
        self.coarse = coarse[:sample_size]

    def fine_selection(self, criterion='t', sample_size=10):
        fine = self.coarse
        fine.sort(key=lambda x: x[1][criterion][0], reverse=True)
        self.fine = fine[:sample_size]



