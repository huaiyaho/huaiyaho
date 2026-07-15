"""
StockPilot Stock SDK Provider

Adapter placeholder for connecting stock-sdk or other market data sources.
All providers should return StockPilot standard market objects.
"""


class StockSDKProvider:
    def __init__(self, client=None):
        self.client = client

    def get_stocks(self):
        """Return stock list in StockPilot format."""
        return []

    def get_daily_prices(self, code, start=None, end=None):
        """Return daily bars in StockPilot format."""
        return []
