"""StockPilot application entry point.

Provides a simple local launcher for the MVP workflow.
"""

from stockpilot.v1.core.scan_pipeline import run_scan


def main():
    print("StockPilot starting...")
    result = run_scan()
    print("Scan completed")
    print(result)


if __name__ == "__main__":
    main()
