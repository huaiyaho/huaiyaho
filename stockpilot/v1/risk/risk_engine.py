"""
StockPilot V1.3.4 Risk Engine
风险识别模块
"""

class RiskEngine:
    def __init__(self):
        pass

    def high_shadow_risk(self, data):
        score = 0
        if data.get("high_position"):
            score += 30
        if data.get("volume_expand"):
            score += 25
        if data.get("close_near_low"):
            score += 25
        if data.get("trend_break"):
            score += 20

        return {
            "risk_score": score,
            "signal": "high_risk" if score >= 60 else "normal"
        }

    def pullback_quality(self, data):
        score = 0

        if data.get("volume_shrink"):
            score += 40
        if data.get("support_hold"):
            score += 40
        if data.get("sector_strong"):
            score += 20

        return {
            "score": score,
            "type": "healthy_pullback" if score >= 70 else "weak_pullback"
        }

    def analyze(self, data):
        shadow = self.high_shadow_risk(data)
        pullback = self.pullback_quality(data)

        return {
            "shadow": shadow,
            "pullback": pullback
        }
