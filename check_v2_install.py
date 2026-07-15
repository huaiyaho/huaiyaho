"""Run a local StockPilot V2 installation and smoke-test check."""

from __future__ import annotations

import argparse
import platform
import sqlite3
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether StockPilot V2 can run locally.")
    parser.add_argument(
        "--keep-db",
        action="store_true",
        help="Keep the temporary smoke-test database under data/ instead of deleting it.",
    )
    args = parser.parse_args()

    checks: list[tuple[str, bool, str]] = []
    checks.append(("Python version", sys.version_info >= (3, 11), platform.python_version()))
    checks.append(("SQLite", sqlite3.sqlite_version_info >= (3, 24, 0), sqlite3.sqlite_version))

    try:
        from stockpilot.v2.domain.models import (
            AssetId,
            AssetType,
            CompanyProfile,
            Market,
        )
        from stockpilot.v2.repositories.sqlite_store import SQLiteResearchRepository

        checks.append(("V2 imports", True, "domain models and repository imported"))
    except Exception as exc:  # pragma: no cover - diagnostic entry point
        checks.append(("V2 imports", False, repr(exc)))
        _print_results(checks)
        return 1

    if args.keep_db:
        database_path = Path("data/install_check_v2.db")
        database_path.unlink(missing_ok=True)
        cleanup = False
    else:
        temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(temporary_directory.name) / "install_check_v2.db"
        cleanup = True

    try:
        repository = SQLiteResearchRepository(database_path)
        profile = CompanyProfile(
            asset_id=AssetId("600000", Market.CN, AssetType.EQUITY),
            name="安装测试公司",
            primary_industry_id="install-test",
            products=("测试产品",),
        )
        repository.save_company_profile(profile)
        restored = repository.get_company_profile(profile.asset_id)
        success = restored == profile
        checks.append(("SQLite round trip", success, str(database_path)))
    except Exception as exc:  # pragma: no cover - diagnostic entry point
        checks.append(("SQLite round trip", False, repr(exc)))
    finally:
        if cleanup:
            temporary_directory.cleanup()

    demo_path = Path("run_v2_demo.py")
    checks.append(("V2 demo entry", demo_path.is_file(), str(demo_path)))
    _print_results(checks)
    return 0 if all(result for _, result, _ in checks) else 1


def _print_results(checks: list[tuple[str, bool, str]]) -> None:
    print("StockPilot V2 installation check")
    print("=" * 48)
    for name, success, detail in checks:
        marker = "PASS" if success else "FAIL"
        print(f"[{marker}] {name}: {detail}")
    print("=" * 48)
    if all(success for _, success, _ in checks):
        print("Environment is ready. Next run: python run_v2_demo.py")
    else:
        print("Environment is not ready. Fix the FAIL items before testing.")


if __name__ == "__main__":
    raise SystemExit(main())
