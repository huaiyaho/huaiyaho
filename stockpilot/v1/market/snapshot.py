"""Market snapshot module.

Stores a daily market state before deeper analysis.
"""

from dataclasses import dataclass, asdict
from datetime import date


@dataclass
class MarketSnapshot:
    trade_date: str
    up_count: int
    down_count: int
    turnover: float
    index_change: float
    market_state: str

    def to_dict(self):
        return asdict(self)


def create_snapshot(up_count, down_count, turnover, index_change):
    if up_count > down_count * 1.5:
        state = "strong"
    elif down_count > up_count * 1.5:
        state = "weak"
    else:
        state = "balanced"

    return MarketSnapshot(
        trade_date=str(date.today()),
        up_count=up_count,
        down_count=down_count,
        turnover=turnover,
        index_change=index_change,
        market_state=state,
    )
