"""StockPilot Event Impact Scoring Engine

Score external events by impact scope, duration, expectation gap and historical relevance.
"""


def score_event(event):
    weights = {
        "scope": 0.35,
        "duration": 0.25,
        "expectation_gap": 0.25,
        "certainty": 0.15,
    }

    score = 0
    for key, weight in weights.items():
        score += event.get(key, 0) * weight

    return round(score, 2)


def classify_strength(score):
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 50:
        return "C"
    return "D"
