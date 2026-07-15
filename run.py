from pathlib import Path

from stockpilot.pipeline import run


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    try:
        outputs = run(project_root)
    except Exception as exc:
        print(f"[StockPilot] Failed: {exc}")
        raise SystemExit(1) from exc

    print("[StockPilot] Snapshot generated successfully:")
    for name, path in outputs.items():
        print(f"  {name}: {path.relative_to(project_root)}")
