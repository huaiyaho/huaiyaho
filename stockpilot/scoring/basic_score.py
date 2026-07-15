"""StockPilot basic scoring model."""


def score_stock(indicators):
    score = 0

    # Trend 40 points
    if indicators.get("ma5") and indicators.get("ma20"):
        if indicators["ma5"] > indicators["ma20"]:
            score += 20
    if indicators.get("ma20") and indicators.get("ma60"):
        if indicators["ma20"] > indicators["ma60"]:
            score += 20

    # Strength 20 points
    change = indicators.get("change_20")
    if change:
        score += min(max(change * 100, 0), 20)

    # Volume 25 points
    vr = indicators.get("volume_ratio")
    if vr:
        score += min(vr * 5, 25)

    # Risk reserve 15 points
    if score < 85:
        score += 5

    return round(min(score, 100), 2)
