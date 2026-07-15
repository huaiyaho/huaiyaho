from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from stockpilot.v2.domain.models import (
    AssetId,
    CompanyProfile,
    Confidence,
    DecisionAction,
    Direction,
    EventType,
    IndustryImpact,
    Market,
    MarketEvent,
    Score,
)
from stockpilot.v2.pipelines.event_research import EventResearchPipeline
from stockpilot.v2.repositories.sqlite_store import SQLiteResearchRepository


class EventResearchPipelineTest(unittest.TestCase):
    def test_pipeline_ranks_related_companies_and_persists_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = SQLiteResearchRepository(Path(temp_dir) / "test.db")
            direct = CompanyProfile(
                asset_id=AssetId("000001", Market.CN),
                name="Direct Beneficiary",
                primary_industry_id="industry_a",
                revenue_exposure={"industry_a": 0.80},
            )
            indirect = CompanyProfile(
                asset_id=AssetId("000002", Market.CN),
                name="Indirect Beneficiary",
                primary_industry_id="industry_a",
                revenue_exposure={"industry_a": 0.35},
            )
            unrelated = CompanyProfile(
                asset_id=AssetId("000003", Market.CN),
                name="Unrelated",
                primary_industry_id="industry_b",
                revenue_exposure={"industry_b": 0.90},
            )
            for profile in (direct, indirect, unrelated):
                repository.save_company_profile(profile)

            event = MarketEvent(
                event_id="event-1",
                event_type=EventType.INDUSTRY,
                title="Demand expansion",
                summary="test",
                occurred_at=datetime.now(timezone.utc),
                direction=Direction.POSITIVE,
            )
            impact = IndustryImpact(
                event_id=event.event_id,
                industry_id="industry_a",
                direction=Direction.POSITIVE,
                impact_score=Score(90, Confidence.HIGH),
                transmission_path=("demand", "industry_a"),
            )

            result = EventResearchPipeline(repository).run(
                event,
                (impact,),
                technical_scores={
                    direct.asset_id.key: 75,
                    indirect.asset_id.key: 75,
                },
                valuation_scores={
                    direct.asset_id.key: 70,
                    indirect.asset_id.key: 70,
                },
            )

            self.assertEqual(2, len(result.assessments))
            self.assertEqual(direct.asset_id, result.assessments[0].asset_id)
            self.assertNotEqual(DecisionAction.AVOID, result.decisions[0].action)
            self.assertEqual(2, len(repository.latest_assessments()))
            self.assertEqual(2, len(repository.latest_decisions()))
            self.assertIsNotNone(repository.get_event(event.event_id))


if __name__ == "__main__":
    unittest.main()
