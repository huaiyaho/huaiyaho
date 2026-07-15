"""Mainline detection engine.

First version: evaluate market themes by heat, breadth and leader strength.
"""


def calculate_mainline_score(theme):
    heat = theme.get("heat", 0)
    breadth = theme.get("breadth", 0)
    leader = theme.get("leader_strength", 0)
    return heat * 0.4 + breadth * 0.3 + leader * 0.3


def rank_mainlines(themes):
    for theme in themes:
        theme["mainline_score"] = calculate_mainline_score(theme)
    return sorted(themes, key=lambda x: x["mainline_score"], reverse=True)
