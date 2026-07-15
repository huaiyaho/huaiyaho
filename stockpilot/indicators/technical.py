"""StockPilot technical indicator engine."""


def moving_average(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def price_change(values, period):
    if len(values) <= period:
        return None
    old = values[-period-1]
    if old == 0:
        return None
    return (values[-1] - old) / old


def volume_ratio(volumes, period=5):
    if len(volumes) <= period:
        return None
    avg = sum(volumes[-period-1:-1]) / period
    if avg == 0:
        return None
    return volumes[-1] / avg


def calculate_basic_indicators(closes, volumes):
    return {
        "ma5": moving_average(closes, 5),
        "ma10": moving_average(closes, 10),
        "ma20": moving_average(closes, 20),
        "ma60": moving_average(closes, 60),
        "change_5": price_change(closes, 5),
        "change_20": price_change(closes, 20),
        "volume_ratio": volume_ratio(volumes),
    }
