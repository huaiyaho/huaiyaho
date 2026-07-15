"""Application service that synchronizes stock-sdk data into SQLite."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from stockpilot.v2.providers.stock_sdk import StockSdkProvider
from stockpilot.v2.repositories.market_data_store import SQLiteMarketDataStore


@dataclass(frozen=True, slots=True)
class SyncResult:
    mode: str
    quote_count: int = 0
    kline_count: int = 0
    started_at: str = ""
    finished_at: str = ""


class MarketSyncService:
    """Coordinate provider reads and idempotent local persistence."""

    def __init__(
        self,
        provider: StockSdkProvider,
        store: SQLiteMarketDataStore,
    ) -> None:
        self.provider = provider
        self.store = store

    def sync_all_cn_quotes(
        self,
        *,
        concurrency: int = 5,
        keep_history: bool = True,
    ) -> SyncResult:
        started = datetime.now(timezone.utc)
        quotes = self.provider.all_cn_quotes(concurrency=concurrency)
        count = self.store.save_quotes(
            quotes,
            observed_at=started,
            keep_history=keep_history,
        )
        return SyncResult(
            mode="all-cn-quotes",
            quote_count=count,
            started_at=started.isoformat(timespec="seconds"),
            finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

    def sync_quotes(
        self,
        symbols: Iterable[str],
        *,
        keep_history: bool = True,
    ) -> SyncResult:
        started = datetime.now(timezone.utc)
        quotes = self.provider.quotes(symbols)
        count = self.store.save_quotes(
            quotes,
            observed_at=started,
            keep_history=keep_history,
        )
        return SyncResult(
            mode="quotes",
            quote_count=count,
            started_at=started.isoformat(timespec="seconds"),
            finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

    def sync_kline(
        self,
        symbol: str,
        *,
        period: str = "daily",
        limit: int = 250,
    ) -> SyncResult:
        started = datetime.now(timezone.utc)
        bars = self.provider.kline(symbol, period=period, limit=limit)
        count = self.store.save_klines(symbol, period, bars)
        return SyncResult(
            mode="kline",
            kline_count=count,
            started_at=started.isoformat(timespec="seconds"),
            finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
