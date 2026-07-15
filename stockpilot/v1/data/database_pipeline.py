"""StockPilot database pipeline.

CSV/imported market data is normalized and stored before analysis.
"""

from datetime import datetime


class DatabasePipeline:
    def __init__(self, storage=None):
        self.storage = storage if storage is not None else []

    def save_records(self, records):
        for record in records:
            item = dict(record)
            item.setdefault("created_at", datetime.utcnow().isoformat())
            self.storage.append(item)
        return len(records)

    def get_records(self):
        return self.storage
