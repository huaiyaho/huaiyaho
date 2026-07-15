"""CLI for synchronizing stock-sdk market data into StockPilot V2 SQLite."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from stockpilot.v2.providers.stock_sdk import StockSdkProvider, StockSdkProviderError
from stockpilot.v2.repositories.market_data_store import SQLiteMarketDataStore
from stockpilot.v2.services.market_sync import MarketSyncService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronize stock-sdk market data")
    parser.add_argument("--database", default="data/stockpilot_v2.db")
    parser.add_argument("--node", default="node")
    parser.add_argument("--timeout", type=int, default=120)

    subparsers = parser.add_subparsers(dest="command", required=True)

    health = subparsers.add_parser("health", help="check Node and stock-sdk bridge")
    health.set_defaults(action="health")

    all_cn = subparsers.add_parser("all-cn", help="sync the current full A-share market")
    all_cn.add_argument("--concurrency", type=int, default=5)
    all_cn.add_argument("--no-history", action="store_true")

    quotes = subparsers.add_parser("quotes", help="sync selected A-share symbols")
    quotes.add_argument("symbols", nargs="+")
    quotes.add_argument("--no-history", action="store_true")

    kline = subparsers.add_parser("kline", help="sync historical bars for one symbol")
    kline.add_argument("symbol")
    kline.add_argument("--period", default="daily")
    kline.add_argument("--limit", type=int, default=250)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    provider = StockSdkProvider(node_binary=args.node, timeout_seconds=args.timeout)

    try:
        if args.command == "health":
            print(json.dumps(provider.check_environment(), ensure_ascii=False, indent=2))
            return 0

        store = SQLiteMarketDataStore(args.database)
        service = MarketSyncService(provider, store)

        if args.command == "all-cn":
            result = service.sync_all_cn_quotes(
                concurrency=args.concurrency,
                keep_history=not args.no_history,
            )
        elif args.command == "quotes":
            result = service.sync_quotes(
                args.symbols,
                keep_history=not args.no_history,
            )
        else:
            result = service.sync_kline(
                args.symbol,
                period=args.period,
                limit=args.limit,
            )

        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return 0
    except (StockSdkProviderError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
