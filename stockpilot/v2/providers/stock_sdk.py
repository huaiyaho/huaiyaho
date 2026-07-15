"""Python adapter for the JavaScript ``stock-sdk`` package.

StockPilot V2 is Python-first, while stock-sdk is a Node.js SDK.  This module
keeps that boundary explicit by invoking a small JSON bridge and returning
normalized Python records.  No investment logic lives in this provider.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


class StockSdkProviderError(RuntimeError):
    """Raised when the Node bridge or upstream stock-sdk request fails."""


@dataclass(frozen=True, slots=True)
class MarketQuote:
    symbol: str
    name: str | None
    price: float | None
    change_percent: float | None
    volume: float | None
    amount: float | None
    turnover_rate: float | None
    market_cap: float | None
    float_market_cap: float | None
    pe: float | None
    pb: float | None
    raw: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class KlineBar:
    date: str
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: float | None
    amount: float | None
    change_percent: float | None
    raw: Mapping[str, Any]


class StockSdkProvider:
    """Call stock-sdk through the repository's Node bridge."""

    def __init__(
        self,
        *,
        project_root: str | Path | None = None,
        node_binary: str = "node",
        timeout_seconds: int = 120,
    ) -> None:
        root = Path(project_root) if project_root else Path(__file__).resolve().parents[3]
        self.project_root = root.resolve()
        self.bridge_path = (
            self.project_root / "stockpilot/v2/providers/stock_sdk_bridge.mjs"
        )
        self.node_binary = node_binary
        self.timeout_seconds = timeout_seconds

    def check_environment(self) -> dict[str, Any]:
        node_path = shutil.which(self.node_binary)
        if not node_path:
            raise StockSdkProviderError(
                "Node.js was not found. Install Node.js 18+ before using stock-sdk."
            )
        if not self.bridge_path.exists():
            raise StockSdkProviderError(f"bridge not found: {self.bridge_path}")
        return self._call({"action": "health"})

    def all_cn_quotes(self, *, concurrency: int = 5) -> list[MarketQuote]:
        if not 1 <= concurrency <= 20:
            raise ValueError("concurrency must be between 1 and 20")
        payload = self._call({"action": "cn_market", "concurrency": concurrency})
        return [self._quote(item) for item in payload.get("data", [])]

    def quotes(self, symbols: Iterable[str]) -> list[MarketQuote]:
        normalized = [str(symbol).strip() for symbol in symbols if str(symbol).strip()]
        if not normalized:
            raise ValueError("symbols must not be empty")
        payload = self._call({"action": "quotes", "symbols": normalized})
        return [self._quote(item) for item in payload.get("data", [])]

    def kline(
        self,
        symbol: str,
        *,
        period: str = "daily",
        limit: int = 250,
    ) -> list[KlineBar]:
        if limit < 1 or limit > 5000:
            raise ValueError("limit must be between 1 and 5000")
        payload = self._call(
            {
                "action": "kline",
                "symbol": symbol,
                "period": period,
                "limit": limit,
            }
        )
        return [self._bar(item) for item in payload.get("data", [])]

    def _call(self, request: Mapping[str, Any]) -> dict[str, Any]:
        command = [self.node_binary, str(self.bridge_path)]
        try:
            completed = subprocess.run(
                command,
                input=json.dumps(request, ensure_ascii=False),
                text=True,
                capture_output=True,
                cwd=self.project_root,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise StockSdkProviderError(
                f"stock-sdk request timed out after {self.timeout_seconds}s"
            ) from exc
        except OSError as exc:
            raise StockSdkProviderError(f"failed to start Node bridge: {exc}") from exc

        stdout = completed.stdout.strip()
        if not stdout:
            detail = completed.stderr.strip() or f"exit code {completed.returncode}"
            raise StockSdkProviderError(f"stock-sdk returned no data: {detail}")

        try:
            payload = json.loads(stdout.splitlines()[-1])
        except json.JSONDecodeError as exc:
            raise StockSdkProviderError(
                f"invalid JSON from stock-sdk: {stdout[-500:]}"
            ) from exc

        if not payload.get("ok"):
            error = payload.get("error") or {}
            message = error.get("message") or completed.stderr.strip() or "unknown error"
            code = error.get("code")
            suffix = f" ({code})" if code else ""
            raise StockSdkProviderError(f"stock-sdk request failed: {message}{suffix}")
        return payload

    @staticmethod
    def _quote(item: Mapping[str, Any]) -> MarketQuote:
        return MarketQuote(
            symbol=str(item.get("symbol") or item.get("code") or "").strip(),
            name=_optional_str(item.get("name")),
            price=_optional_float(item.get("price")),
            change_percent=_optional_float(item.get("changePercent")),
            volume=_optional_float(item.get("volume")),
            amount=_optional_float(item.get("amount")),
            turnover_rate=_optional_float(item.get("turnoverRate")),
            market_cap=_optional_float(item.get("marketCap")),
            float_market_cap=_optional_float(item.get("floatMarketCap")),
            pe=_optional_float(item.get("pe")),
            pb=_optional_float(item.get("pb")),
            raw=item.get("raw") if isinstance(item.get("raw"), Mapping) else dict(item),
        )

    @staticmethod
    def _bar(item: Mapping[str, Any]) -> KlineBar:
        return KlineBar(
            date=str(item.get("date") or ""),
            open=_optional_float(item.get("open")),
            high=_optional_float(item.get("high")),
            low=_optional_float(item.get("low")),
            close=_optional_float(item.get("close")),
            volume=_optional_float(item.get("volume")),
            amount=_optional_float(item.get("amount")),
            change_percent=_optional_float(item.get("changePercent")),
            raw=item.get("raw") if isinstance(item.get("raw"), Mapping) else dict(item),
        )


def _optional_float(value: Any) -> float | None:
    if value in (None, "", "--", "-"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
