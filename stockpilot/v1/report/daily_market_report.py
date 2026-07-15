"""Generate first version daily market report."""


def generate_report(snapshot, themes=None, stocks=None):
    themes = themes or []
    stocks = stocks or []

    lines = [
        "# StockPilot Daily Report",
        "",
        f"Date: {snapshot.trade_date}",
        f"Market: {snapshot.market_state}",
        f"Up: {snapshot.up_count} Down: {snapshot.down_count}",
        f"Turnover: {snapshot.turnover}",
        "",
        "## Hot Themes",
    ]

    lines.extend([f"- {x}" for x in themes])
    lines.append("")
    lines.append("## Top Stocks")
    lines.extend([f"- {x}" for x in stocks])

    return "\n".join(lines)
