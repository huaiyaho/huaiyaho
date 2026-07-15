"""
StockPilot V1.6.5 Strategy Report
Generate evaluation summaries from backtest results.
"""


class StrategyReport:
    def generate(self, result):
        return {
            "strategy": result.get("strategy", "unknown"),
            "period": result.get("period", {}),
            "performance": {
                "return": result.get("return", 0),
                "max_drawdown": result.get("max_drawdown", 0),
                "win_rate": result.get("win_rate", 0),
                "trades": result.get("trades", 0),
            },
            "summary": self._summary(result),
        }

    def _summary(self, result):
        score = 0
        score += 1 if result.get("return", 0) > 0 else 0
        score += 1 if result.get("win_rate", 0) > 0.5 else 0
        score += 1 if result.get("max_drawdown", 1) < 0.3 else 0

        if score >= 3:
            return "策略表现优秀"
        if score == 2:
            return "策略表现中等，需要优化"
        return "策略需要进一步验证"
