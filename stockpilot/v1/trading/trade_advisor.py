"""
StockPilot V1.3.3 Trade Advisor

Combine market, theme, leader cycle and risk signals
into a structured trading state.
"""


class TradeAdvisor:
    def evaluate(self, stock):
        score = stock.get("score", 0)
        stage = stock.get("stage", "unknown")
        risk = stock.get("risk", "medium")

        if score >= 85 and stage in ["rising", "acceleration"] and risk != "high":
            action = "关注"
        elif stage == "divergence":
            action = "等待分歧承接"
        elif stage == "retreat" or risk == "high":
            action = "规避"
        else:
            action = "观察"

        return {
            "code": stock.get("code"),
            "name": stock.get("name"),
            "score": score,
            "stage": stage,
            "risk": risk,
            "action": action,
        }
