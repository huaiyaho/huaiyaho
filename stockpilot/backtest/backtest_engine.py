"""StockPilot simple backtest framework."""


def run_backtest(signals, prices):
    results = []
    for signal in signals:
        code = signal.get("code")
        results.append({
            "code": code,
            "matched": code in prices
        })
    return results
