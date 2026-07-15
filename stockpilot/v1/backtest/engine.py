"""
StockPilot V1.6 Backtest Engine

Basic historical simulation framework.
"""

class BacktestEngine:
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.trades = []

    def run(self, signals, prices):
        capital = self.initial_capital
        position = None

        for date, signal in signals.items():
            price = prices.get(date)
            if price is None:
                continue

            if signal == "buy" and position is None:
                position = {"date": date, "price": price}

            elif signal == "sell" and position:
                pnl = price / position["price"] - 1
                self.trades.append({
                    "entry": position["date"],
                    "exit": date,
                    "return": pnl
                })
                position = None

        return self.trades
