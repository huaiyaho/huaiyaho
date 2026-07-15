"""Scheduled market data synchronization."""

class SyncJob:
    def __init__(self, importer):
        self.importer = importer

    def run(self):
        stocks = self.importer.sync_stocks()
        codes = [s.get('code') for s in stocks]
        return self.importer.sync_daily(codes)
