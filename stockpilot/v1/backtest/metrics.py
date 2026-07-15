"""StockPilot backtest metrics.

Provides basic performance statistics for strategy evaluation.
"""


def calculate_metrics(trades, initial_capital=1000000):
    """Calculate basic backtest metrics from trade results."""
    if not trades:
        return {
            "return": 0,
            "win_rate": 0,
            "max_drawdown": 0,
            "trade_count": 0,
        }

    profits = [t.get("profit", 0) for t in trades]
    wins = [p for p in profits if p > 0]

    equity = initial_capital
    peak = equity
    max_drawdown = 0

    for profit in profits:
        equity += profit
        peak = max(peak, equity)
        drawdown = (peak - equity) / peak if peak else 0
        max_drawdown = max(max_drawdown, drawdown)

    return {
        "return": (equity - initial_capital) / initial_capital,
        "win_rate": len(wins) / len(profits),
        "max_drawdown": max_drawdown,
        "trade_count": len(trades),
    }
