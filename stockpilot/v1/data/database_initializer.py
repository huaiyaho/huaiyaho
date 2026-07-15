"""StockPilot database initialization utilities."""

from datetime import datetime


def initialize_market_tables():
    """Prepare tables required for market data ingestion.

    Placeholder for database migration logic.
    """
    return {
        "status": "ready",
        "initialized_at": datetime.utcnow().isoformat()
    }
