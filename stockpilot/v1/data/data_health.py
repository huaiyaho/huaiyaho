"""Data quality checks for StockPilot."""


def check_bar(bar):
    required = ["code", "close"]
    return all(k in bar for k in required)


def check_dataset(rows):
    if not rows:
        return False
    return all(check_bar(row) for row in rows)
