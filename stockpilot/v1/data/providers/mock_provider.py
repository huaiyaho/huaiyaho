"""Mock data provider for pipeline testing."""

from datetime import date


def get_sample_bars():
    return [
        {
            "code": "000001",
            "name": "Sample",
            "trade_date": str(date.today()),
            "open": 10,
            "high": 10.5,
            "low": 9.8,
            "close": 10.2,
            "volume": 1000000,
            "amount": 10200000,
        }
    ]
