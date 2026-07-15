"""Stock SDK provider adapter.

This module converts external market providers into StockPilot models.
"""

from datetime import date
from ..models import DailyBar, StockInfo


class StockSDKProvider:
    """Adapter placeholder for stock-sdk integration."""

    def get_stocks(self) -> list[StockInfo]:
        """Return normalized stock list."""
        return []

    def get_daily_prices(self, code: str, start: date, end: date) -> list[DailyBar]:
        """Return normalized daily bars."""
        return []
