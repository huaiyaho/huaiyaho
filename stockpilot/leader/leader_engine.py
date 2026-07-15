"""StockPilot leader identification engine."""


def calculate_leader_score(stock):
    """Calculate a relative leader score inside a theme."""
    return (
        stock.get("trend_score", 0) * 0.35
        + stock.get("volume_score", 0) * 0.25
        + stock.get("strength_score", 0) * 0.25
        + stock.get("market_position", 0) * 0.15
    )


def classify_role(score):
    if score >= 85:
        return "leader"
    if score >= 70:
        return "core"
    return "follower"
