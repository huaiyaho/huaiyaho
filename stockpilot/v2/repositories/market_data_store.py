"""SQLite persistence for normalized market data.

This store is intentionally separate from the research repository: market data has
higher write volume and a different retention lifecycle. Quotes are stored both as
a latest snapshot and as timestamped history; kline bars are idempotent by
symbol/period/date.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

from stockpilot.v2.providers.stock_sdk import KlineBar, MarketQuote


class SQLiteMarketDataStore:
    """Persist normalized stock-sdk quotes and kline bars in SQLite."""

    def __init__(self, database_path: str | Path = "data/stockpilot_v2.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS market_quotes_latest (
                    symbol TEXT PRIMARY KEY,
                    name TEXT,
                    price REAL,
                    change_percent REAL,
                    volume REAL,
                    amount REAL,
                    turnover_rate REAL,
                    market_cap REAL,
                    float_market_cap REAL,
                    pe REAL,
                    pb REAL,
                    payload_json TEXT NOT NULL,
                    observed_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_quotes_latest_change
                    ON market_quotes_latest(change_percent DESC);
                CREATE INDEX IF NOT EXISTS idx_quotes_latest_amount
                    ON market_quotes_latest(amount DESC);

                CREATE TABLE IF NOT EXISTS market_quote_history (
                    symbol TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    price REAL,
                    change_percent REAL,
                    amount REAL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(symbol, observed_at)
                );
                CREATE INDEX IF NOT EXISTS idx_quote_history_time
                    ON market_quote_history(observed_at DESC);

                CREATE TABLE IF NOT EXISTS market_klines (
                    symbol TEXT NOT NULL,
                    period TEXT NOT NULL,
                    bar_date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    amount REAL,
                    change_percent REAL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(symbol, period, bar_date)
                );
                CREATE INDEX IF NOT EXISTS idx_klines_symbol_date
                    ON market_klines(symbol, period, bar_date DESC);
                """
            )

    def save_quotes(
        self,
        quotes: Iterable[MarketQuote],
        *,
        observed_at: datetime | None = None,
        keep_history: bool = True,
    ) -> int:
        timestamp = _iso_timestamp(observed_at)
        rows = list(quotes)
        if not rows:
            return 0

        with self.connection() as connection:
            for quote in rows:
                payload = json.dumps(asdict(quote), ensure_ascii=False, separators=(",", ":"))
                values = (
                    quote.symbol,
                    quote.name,
                    quote.price,
                    quote.change_percent,
                    quote.volume,
                    quote.amount,
                    quote.turnover_rate,
                    quote.market_cap,
                    quote.float_market_cap,
                    quote.pe,
                    quote.pb,
                    payload,
                    timestamp,
                )
                connection.execute(
                    """
                    INSERT INTO market_quotes_latest(
                        symbol, name, price, change_percent, volume, amount,
                        turnover_rate, market_cap, float_market_cap, pe, pb,
                        payload_json, observed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(symbol) DO UPDATE SET
                        name = excluded.name,
                        price = excluded.price,
                        change_percent = excluded.change_percent,
                        volume = excluded.volume,
                        amount = excluded.amount,
                        turnover_rate = excluded.turnover_rate,
                        market_cap = excluded.market_cap,
                        float_market_cap = excluded.float_market_cap,
                        pe = excluded.pe,
                        pb = excluded.pb,
                        payload_json = excluded.payload_json,
                        observed_at = excluded.observed_at
                    """,
                    values,
                )
                if keep_history:
                    connection.execute(
                        """
                        INSERT OR REPLACE INTO market_quote_history(
                            symbol, observed_at, price, change_percent, amount, payload_json
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            quote.symbol,
                            timestamp,
                            quote.price,
                            quote.change_percent,
                            quote.amount,
                            payload,
                        ),
                    )
        return len(rows)

    def save_klines(self, symbol: str, period: str, bars: Iterable[KlineBar]) -> int:
        rows = list(bars)
        if not rows:
            return 0
        updated_at = _iso_timestamp(None)
        with self.connection() as connection:
            for bar in rows:
                if not bar.date:
                    continue
                payload = json.dumps(asdict(bar), ensure_ascii=False, separators=(",", ":"))
                connection.execute(
                    """
                    INSERT INTO market_klines(
                        symbol, period, bar_date, open, high, low, close,
                        volume, amount, change_percent, payload_json, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(symbol, period, bar_date) DO UPDATE SET
                        open = excluded.open,
                        high = excluded.high,
                        low = excluded.low,
                        close = excluded.close,
                        volume = excluded.volume,
                        amount = excluded.amount,
                        change_percent = excluded.change_percent,
                        payload_json = excluded.payload_json,
                        updated_at = excluded.updated_at
                    """,
                    (
                        symbol,
                        period,
                        bar.date,
                        bar.open,
                        bar.high,
                        bar.low,
                        bar.close,
                        bar.volume,
                        bar.amount,
                        bar.change_percent,
                        payload,
                        updated_at,
                    ),
                )
        return sum(1 for bar in rows if bar.date)

    def latest_quotes(self, *, limit: int = 100, order_by: str = "amount") -> list[dict]:
        allowed = {"amount", "change_percent", "market_cap", "symbol"}
        if order_by not in allowed:
            raise ValueError(f"order_by must be one of: {', '.join(sorted(allowed))}")
        if not 1 <= limit <= 100_000:
            raise ValueError("limit must be between 1 and 100000")
        direction = "ASC" if order_by == "symbol" else "DESC"
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT payload_json, observed_at FROM market_quotes_latest "
                f"ORDER BY {order_by} {direction} LIMIT ?",
                (limit,),
            ).fetchall()
        result: list[dict] = []
        for row in rows:
            payload = json.loads(str(row["payload_json"]))
            payload["observed_at"] = row["observed_at"]
            result.append(payload)
        return result


def _iso_timestamp(value: datetime | None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).isoformat(timespec="seconds")
