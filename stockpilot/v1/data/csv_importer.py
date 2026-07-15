"""
StockPilot CSV Importer
Support first version of Tonghuashun exported market data.
"""

import csv
from pathlib import Path
from datetime import datetime


class CSVImporter:
    def __init__(self):
        self.records = []

    def detect_file(self, file_path):
        return Path(file_path).suffix.lower() == '.csv'

    def load(self, file_path):
        rows = []
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        self.records = rows
        return rows

    def normalize(self, rows):
        result = []
        for row in rows:
            result.append({
                'code': row.get('代码') or row.get('code'),
                'name': row.get('名称') or row.get('name'),
                'date': row.get('日期') or datetime.now().strftime('%Y-%m-%d'),
                'close': row.get('收盘') or row.get('close'),
                'volume': row.get('成交量') or row.get('volume')
            })
        return result
