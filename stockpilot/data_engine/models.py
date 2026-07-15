"""StockPilot market data models.

Unified internal format independent from external providers.
"""
from dataclasses import dataclass
from datetime import date


@dataclass
class DailyBar:
    code: str
    name: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float = 0
    amount: float = 0


@dataclass
class StockInfo:
    code: str
    name: str
    market: str = "CN"
    industry: str = ""
    themes: list[str] | None = None
