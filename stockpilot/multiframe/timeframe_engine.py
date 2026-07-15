"""StockPilot multi timeframe analysis engine."""

from dataclasses import dataclass


@dataclass
class TimeframeSignal:
    daily: str
    weekly: str
    monthly: str
    score: float


def analyze_timeframes(daily_score, weekly_score, monthly_score):
    score = daily_score * 0.5 + weekly_score * 0.3 + monthly_score * 0.2
    return TimeframeSignal(
        daily="strong" if daily_score >= 70 else "weak",
        weekly="strong" if weekly_score >= 70 else "weak",
        monthly="strong" if monthly_score >= 70 else "weak",
        score=round(score, 2),
    )
