"""SQLite storage layer for StockPilot."""
import sqlite3


class StockDatabase:
    def __init__(self, path="stockpilot.db"):
        self.conn = sqlite3.connect(path)
        self.init_tables()

    def init_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_price(
            code TEXT,
            name TEXT,
            trade_date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            amount REAL
        )
        """)
        self.conn.commit()

    def insert_bar(self, bar):
        self.conn.execute(
            "INSERT INTO daily_price VALUES (?,?,?,?,?,?,?,?,?)",
            (bar.code, bar.name, str(bar.trade_date), bar.open,
             bar.high, bar.low, bar.close, bar.volume, bar.amount)
        )
        self.conn.commit()
