"""StockPilot V1.1 data import pipeline."""

class DataImporter:
    def __init__(self, provider, storage):
        self.provider = provider
        self.storage = storage

    def sync_stocks(self):
        stocks = self.provider.get_stocks()
        return stocks

    def sync_daily(self, symbols):
        bars = self.provider.get_daily_prices(symbols)
        return bars
