"""
StockPilot V1.3.5
Intraday support analysis engine

用于判断强势股票回踩时是承接还是走弱。
"""


def analyze_pullback(data):
    """分析盘中回踩质量"""
    score = 0

    if data.get("volume_shrink"):
        score += 30

    if data.get("support_hold"):
        score += 30

    if data.get("afternoon_recover"):
        score += 20

    if data.get("sector_strength"):
        score += 20

    if score >= 75:
        signal = "healthy_pullback"
    elif score >= 50:
        signal = "observe"
    else:
        signal = "weak_pullback"

    return {
        "score": score,
        "signal": signal
    }
