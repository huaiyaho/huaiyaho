"""
StockPilot V1.5.2 Daily Market Report Engine
Generate structured daily market research summary.
"""

from datetime import date


class DailyReportEngine:
    def generate(self, market, themes, stocks, risks=None):
        return {
            "date": str(date.today()),
            "market": market,
            "themes": themes,
            "top_stocks": stocks,
            "risks": risks or [],
            "summary": self._build_summary(market, themes)
        }

    def _build_summary(self, market, themes):
        status = market.get("status", "unknown")
        main_theme = themes[0]["name"] if themes else "none"
        return f"Market status: {status}. Main theme: {main_theme}."
