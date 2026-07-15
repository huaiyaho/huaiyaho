"""
StockPilot V1.8.3 Web UI
Dashboard presentation layer.
"""

from datetime import datetime


def render_dashboard(data=None):
    data = data or {}

    market = data.get("market", {})
    themes = data.get("themes", [])
    stocks = data.get("stocks", [])
    risks = data.get("risks", [])

    return {
        "title": "StockPilot Dashboard",
        "time": datetime.now().isoformat(),
        "market": market,
        "themes": themes,
        "stocks": stocks,
        "risks": risks,
    }


def stock_detail(stock):
    return {
        "name": stock.get("name"),
        "score": stock.get("score", 0),
        "industry": stock.get("industry", []),
        "stage": stock.get("stage", "unknown"),
        "risk": stock.get("risk", "unknown"),
    }
