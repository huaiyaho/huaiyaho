"""StockPilot risk evaluation module."""


def risk_score(stock):
    score = 100
    if stock.get("high_position"):
        score -= 20
    if stock.get("volume_divergence"):
        score -= 20
    if stock.get("trend_break"):
        score -= 30
    return max(score, 0)
