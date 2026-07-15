"""
StockPilot V1.4 Industry Cycle Engine
产业趋势周期模型第一版
"""


class IndustryCycleEngine:
    """Evaluate industry trend stage."""

    STAGES = [
        "technology_breakthrough",
        "expectation_pricing",
        "capital_expansion",
        "earnings_validation",
        "cooling"
    ]

    def analyze(self, data):
        score = 0

        score += data.get("technology", 0) * 0.25
        score += data.get("policy", 0) * 0.15
        score += data.get("capital", 0) * 0.25
        score += data.get("earnings", 0) * 0.20
        score += data.get("valuation", 0) * 0.15

        if score >= 85:
            stage = "capital_expansion"
        elif score >= 70:
            stage = "expectation_pricing"
        elif score >= 50:
            stage = "earnings_validation"
        else:
            stage = "cooling"

        return {
            "score": round(score, 2),
            "stage": stage
        }
