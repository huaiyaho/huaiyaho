"""StockPilot entry and exit signal framework."""


def evaluate_position(trend, volume, risk):
    if risk > 80:
        return "risk"
    if trend >= 80 and volume >= 70:
        return "watch_entry"
    if trend >= 60:
        return "observe"
    return "avoid"
