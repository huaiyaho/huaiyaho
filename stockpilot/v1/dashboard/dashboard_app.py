"""StockPilot V1.8.2 Dashboard MVP data layer."""

from datetime import datetime


def build_dashboard(scan_result=None):
    data = scan_result or {}
    return {
        "title": "StockPilot",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market": data.get("market", {}),
        "themes": data.get("themes", []),
        "stocks": data.get("stocks", []),
        "risks": data.get("risks", []),
    }


if __name__ == "__main__":
    print(build_dashboard())
