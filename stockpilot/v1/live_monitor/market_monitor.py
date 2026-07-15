"""
StockPilot V1.7.1 Live Market Monitor

实时监控基础模块
"""

from datetime import datetime


class MarketMonitor:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, symbol, detail):
        self.events.append({
            "time": datetime.now().isoformat(),
            "type": event_type,
            "symbol": symbol,
            "detail": detail,
        })

    def scan(self, market_data):
        signals = []

        for item in market_data:
            if item.get("volume_expand") and item.get("price_strength"):
                signals.append({
                    "symbol": item.get("symbol"),
                    "signal": "active_breakout",
                    "reason": "放量上涨"
                })

            if item.get("trend_break"):
                signals.append({
                    "symbol": item.get("symbol"),
                    "signal": "risk_warning",
                    "reason": "趋势破坏"
                })

        return signals
