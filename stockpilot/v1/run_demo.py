"""StockPilot V1 demo runner."""

from data.providers.provider_factory import get_provider


def run():
    provider = get_provider()
    bars = provider()
    return {
        "status": "ok",
        "count": len(bars),
        "sample": bars[0] if bars else None,
    }


if __name__ == "__main__":
    print(run())
