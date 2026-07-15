"""Base interface for market data providers."""
from abc import ABC, abstractmethod


class MarketProvider(ABC):
    @abstractmethod
    def get_stocks(self):
        pass

    @abstractmethod
    def get_daily_prices(self, code):
        pass
