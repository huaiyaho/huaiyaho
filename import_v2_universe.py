"""Command-line entry point for importing a real A-share stock universe CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

from stockpilot.v2.ingestion.stock_universe_csv import import_stock_universe_csv
from stockpilot.v2.repositories.sqlite_store import SQLiteResearchRepository


def main() -> int:
    parser = argparse.ArgumentParser(description="Import an A-share stock universe into StockPilot V2.")
    parser.add_argument("csv_file", type=Path, help="CSV containing at least stock code and stock name")
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("data/stockpilot_v2.db"),
        help="SQLite database path (default: data/stockpilot_v2.db)",
    )
    parser.add_argument("--encoding", help="Force CSV encoding, for example utf-8-sig or gb18030")
    args = parser.parse_args()

    repository = SQLiteResearchRepository(args.database)
    summary = import_stock_universe_csv(
        args.csv_file,
        repository,
        encoding=args.encoding,
    )

    print("StockPilot V2 stock universe import")
    print("=" * 48)
    print(f"Source: {args.csv_file}")
    print(f"Database: {args.database}")
    print(f"Rows read: {summary.rows_read}")
    print(f"Companies saved: {summary.companies_saved}")
    print(f"Industries saved: {summary.industries_saved}")
    print(f"Rows skipped: {summary.rows_skipped}")
    if summary.warnings:
        print("Warnings:")
        for warning in summary.warnings[:20]:
            print(f"- {warning}")
        if len(summary.warnings) > 20:
            print(f"- ... and {len(summary.warnings) - 20} more")
    return 0 if summary.companies_saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
