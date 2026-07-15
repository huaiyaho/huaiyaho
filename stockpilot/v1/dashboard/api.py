"""StockPilot V1 Dashboard API layer.

Provides unified read interfaces for market, themes and stocks.
"""


def get_market_summary(snapshot):
    return {
        "status": snapshot.get("status", "unknown"),
        "up_count": snapshot.get("up_count", 0),
        "down_count": snapshot.get("down_count", 0),
        "turnover": snapshot.get("turnover", 0),
    }


def get_theme_ranking(themes):
    return sorted(themes, key=lambda x: x.get("score", 0), reverse=True)


def get_stock_ranking(stocks, limit=20):
    return sorted(stocks, key=lambda x: x.get("score", 0), reverse=True)[:limit]
