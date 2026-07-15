"""StockPilot scheduled task runner.

Responsible for daily pipeline execution.
"""


def run_daily_tasks():
    return {
        "status": "ready",
        "tasks": [
            "update_market_data",
            "calculate_scores",
            "generate_report"
        ]
    }
