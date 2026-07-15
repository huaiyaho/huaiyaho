"""
StockPilot V1.6.4 Historical Replay Engine

Replay historical market days and run strategies step by step.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ReplayResult:
    start_date: str
    end_date: str
    signals: List[Dict[str, Any]] = field(default_factory=list)
    trades: List[Dict[str, Any]] = field(default_factory=list)


class HistoricalReplayEngine:
    """Historical market replay framework."""

    def __init__(self, strategy=None):
        self.strategy = strategy

    def run(self, market_days: List[Dict[str, Any]], start_date: str, end_date: str):
        result = ReplayResult(start_date=start_date, end_date=end_date)

        for day in market_days:
            if self.strategy:
                signal = self.strategy.evaluate(day)
                if signal:
                    result.signals.append(signal)

        return result

    def summary(self, result: ReplayResult):
        return {
            "period": {
                "start": result.start_date,
                "end": result.end_date,
            },
            "signal_count": len(result.signals),
            "trade_count": len(result.trades),
        }
