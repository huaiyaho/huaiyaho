"""StockPilot V1.9.3 Daily Report Engine

Generate daily market summaries from snapshot and change data.
"""

from datetime import datetime


def build_daily_report(snapshot=None, changes=None):
    snapshot = snapshot or {}
    changes = changes or {}

    return {
        "date": snapshot.get("date", datetime.now().strftime("%Y-%m-%d")),
        "market": snapshot.get("market", "unknown"),
        "themes": snapshot.get("themes", []),
        "top_stocks": snapshot.get("stocks", []),
        "changes": changes,
        "risks": snapshot.get("risks", []),
    }


def format_report(report):
    lines = [
        "StockPilot Daily Report",
        f"Date: {report.get('date')}",
        f"Market: {report.get('market')}",
        "",
        "Themes:",
    ]

    for theme in report.get("themes", []):
        lines.append(f"- {theme}")

    lines.append("")
    lines.append("Top Stocks:")
    for stock in report.get("top_stocks", []):
        lines.append(f"- {stock}")

    return "\n".join(lines)
