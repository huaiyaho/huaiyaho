"""
StockPilot CLI Entry
V1.8.5

Commands:
- scan: run market scan pipeline
- report: show latest report
"""

import argparse
from datetime import datetime


def run_scan():
    return {
        "status": "completed",
        "time": datetime.now().isoformat(),
        "message": "StockPilot scan pipeline executed"
    }


def show_report():
    return {
        "status": "ready",
        "message": "Latest StockPilot report"
    }


def main():
    parser = argparse.ArgumentParser(description="StockPilot CLI")
    parser.add_argument("command", choices=["scan", "report"])
    args = parser.parse_args()

    if args.command == "scan":
        print(run_scan())
    elif args.command == "report":
        print(show_report())


if __name__ == "__main__":
    main()
