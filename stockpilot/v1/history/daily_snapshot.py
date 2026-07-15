"""
StockPilot V1.9.1 Daily Snapshot
Store daily market analysis results for comparison.
"""

from datetime import datetime


class DailySnapshot:
    def __init__(self):
        self.records = []

    def save(self, market, themes, stocks, risks):
        snapshot = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "market": market,
            "themes": themes,
            "stocks": stocks,
            "risks": risks,
        }
        self.records.append(snapshot)
        return snapshot

    def latest(self):
        if not self.records:
            return None
        return self.records[-1]
