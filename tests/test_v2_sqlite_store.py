from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from stockpilot.v2.domain.models import (
    AssetId,
    CompanyProfile,
    Confidence,
    Direction,
    EventType,
    Market,
    MarketEvent,
    Score,
)
from stockpilot.v2.repositories import SQLiteResearchRepository


class SQLiteResearchRepositoryTest(unittest.TestCase):
    def test_event_and_company_profile_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = SQLiteResearchRepository(Path(temp_dir) / "stockpilot.db")

            event = MarketEvent(
                event_id="event-1",
                event_type=EventType.INDUSTRY,
                title="Industry demand improves",
                summary="Demand and pricing both improved.",
                occurred_at=datetime(2026, 7, 15, tzinfo=timezone.utc),
                direction=Direction.POSITIVE,
                markets=(Market.CN, Market.US),
                impact_score=Score(
                    88,
                    Confidence.HIGH,
                    ("broad impact", "high certainty"),
                ),
            )
            repository.save_event(event)
            self.assertEqual(repository.get_event("event-1"), event)
            self.assertEqual(repository.list_events(), [event])

            profile = CompanyProfile(
                asset_id=AssetId("688008", Market.CN),
                name="Test Company",
                primary_industry_id="semiconductor",
                industry_ids=("semiconductor", "memory-interface"),
                products=("interface chip",),
                revenue_exposure={"memory-interface": 0.75},
            )
            repository.save_company_profile(profile)
            self.assertEqual(
                repository.get_company_profile(profile.asset_id),
                profile,
            )
            self.assertEqual(
                repository.list_company_profiles(
                    primary_industry_id="semiconductor"
                ),
                [profile],
            )


if __name__ == "__main__":
    unittest.main()
