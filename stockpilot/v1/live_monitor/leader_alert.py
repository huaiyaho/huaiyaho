"""
StockPilot V1.7.2 Leader Alert
龙头异动监控第一版
"""


def detect_leader_strength(data):
    """判断龙头强化信号"""
    score = 0
    if data.get("price_strength"):
        score += 30
    if data.get("sector_follow"):
        score += 30
    if data.get("volume_confirm"):
        score += 40

    return {
        "score": score,
        "signal": "leader_strength" if score >= 70 else "normal"
    }


def detect_leader_weakness(data):
    """判断龙头走弱信号"""
    score = 0
    if data.get("break_support"):
        score += 40
    if data.get("sector_drop"):
        score += 30
    if data.get("volume_sell"):
        score += 30

    return {
        "score": score,
        "signal": "leader_risk" if score >= 70 else "normal"
    }
