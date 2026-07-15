"""StockPilot market report generator."""
from datetime import date


def generate_report(ranking, report_date=None):
    report_date = report_date or str(date.today())

    lines = []
    lines.append("# StockPilot Daily Report")
    lines.append("")
    lines.append(f"Date: {report_date}")
    lines.append("")
    lines.append("## Top Stocks")
    lines.append("")

    for idx, item in enumerate(ranking[:20], 1):
        lines.append(
            f"{idx}. {item.get('name', '')} "
            f"({item.get('code', '')}) - Score: {item.get('score', 0)}"
        )

    return "\n".join(lines)
