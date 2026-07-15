"""
StockPilot V1.3.2 Leader Lifecycle Engine

Identify the lifecycle stage of a market theme leader.
"""


def calculate_cycle_score(data):
    """Calculate lifecycle score from normalized indicators."""
    return (
        data.get("momentum", 0) * 0.3
        + data.get("volume", 0) * 0.25
        + data.get("breadth", 0) * 0.25
        + data.get("stability", 0) * 0.2
    )


def identify_stage(score):
    if score >= 85:
        return "acceleration"
    if score >= 70:
        return "rising"
    if score >= 50:
        return "divergence"
    return "retreat"


def analyze_leader(data):
    score = calculate_cycle_score(data)
    return {
        "score": round(score, 2),
        "stage": identify_stage(score)
    }
