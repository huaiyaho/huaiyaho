"""
StockPilot V1.9 Automation Scheduler

Provides a lightweight scheduling layer for daily scan and report tasks.
"""

from datetime import datetime


class StockPilotScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, name, run_time, callback):
        self.jobs.append({
            "name": name,
            "run_time": run_time,
            "callback": callback,
        })

    def list_jobs(self):
        return self.jobs

    def run_job(self, name):
        for job in self.jobs:
            if job["name"] == name:
                result = job["callback"]()
                return {
                    "job": name,
                    "time": datetime.now().isoformat(),
                    "result": result,
                }
        return {"error": "job_not_found"}


def default_schedule():
    return {
        "morning_scan": "09:00",
        "market_review": "15:30",
    }
