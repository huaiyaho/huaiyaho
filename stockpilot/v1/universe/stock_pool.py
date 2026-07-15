"""StockPilot stock universe management.

Maintains the market universe, tags and filtering helpers.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class StockInfo:
    code: str
    name: str
    industry: str = ""
    tags: List[str] = field(default_factory=list)
    is_leader: bool = False


class StockPool:
    def __init__(self):
        self.stocks: Dict[str, StockInfo] = {}

    def add(self, stock: StockInfo):
        self.stocks[stock.code] = stock

    def get_by_tag(self, tag: str):
        return [s for s in self.stocks.values() if tag in s.tags]

    def leaders(self):
        return [s for s in self.stocks.values() if s.is_leader]

    def size(self):
        return len(self.stocks)
