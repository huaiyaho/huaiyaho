# StockPilot V0.2

StockPilot is a local-first portfolio data pipeline for turning exported CSV/XLSX files into standardized snapshots that can be reviewed by ChatGPT.

## Current capabilities

- Import CSV and XLSX portfolio files
- Recognize common Chinese and English column names
- Normalize stock code, name, quantity, cost and current price
- Calculate market value, floating P/L and return rate
- Generate CSV, JSON and Markdown snapshots
- Keep raw exports and secrets out of Git

## Quick start

1. Install Python 3.11+.
2. Run `pip install -r requirements.txt`.
3. Put an exported portfolio file into `data/raw/`.
4. Run:

```bash
python run.py
```

Windows users can double-click `run_stockpilot.bat`.

Generated files are written to:

- `data/processed/latest_positions.csv`
- `data/snapshots/latest_snapshot.json`
- `data/snapshots/latest_report.md`

## Expected fields

StockPilot automatically maps common fields such as:

- 证券代码 / 股票代码 / code
- 证券名称 / 股票名称 / name
- 股票余额 / 持仓数量 / quantity
- 成本价 / cost
- 最新价 / 当前价 / price

## Important

StockPilot does not connect to a brokerage account and does not place trades. Raw exports may contain sensitive information and are ignored by Git by default.
