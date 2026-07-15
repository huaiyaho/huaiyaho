"""StockPilot data loading pipeline."""

from .database import StockDatabase


class DataLoader:
    def __init__(self, provider, database=None):
        self.provider = provider
        self.database = database or StockDatabase()

    def load_stocks(self):
        return self.provider.get_stocks()

    def load_daily(self, code, start, end):
        bars = self.provider.get_daily_prices(code, start, end)
        for bar in bars:
            self.database.insert_bar(bar)
        return len(bars)
