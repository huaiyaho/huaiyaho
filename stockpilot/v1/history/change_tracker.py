"""
StockPilot V1.9.2 Change Tracker
Compare daily snapshots and identify market/theme/stock changes.
"""

from typing import Dict, List


def compare_rank(old: List[str], new: List[str]) -> Dict[str, Dict]:
    old_map = {name: i + 1 for i, name in enumerate(old)}
    new_map = {name: i + 1 for i, name in enumerate(new)}

    result = {}
    for name in set(old_map) | set(new_map):
        result[name] = {
            "old_rank": old_map.get(name),
            "new_rank": new_map.get(name),
            "change": None,
        }

        if old_map.get(name) and new_map.get(name):
            result[name]["change"] = old_map[name] - new_map[name]
        elif new_map.get(name):
            result[name]["change"] = "new"
        else:
            result[name]["change"] = "removed"

    return result


def track_snapshot(previous: Dict, current: Dict) -> Dict:
    return {
        "theme_change": compare_rank(
            previous.get("themes", []),
            current.get("themes", []),
        ),
        "stock_change": compare_rank(
            previous.get("stocks", []),
            current.get("stocks", []),
        ),
        "market_change": {
            "previous": previous.get("market"),
            "current": current.get("market"),
        },
    }
