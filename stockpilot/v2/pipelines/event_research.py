"""Runnable V2 event-to-decision vertical slice.

This module intentionally uses deterministic, explainable rules.  It is the first
end-to-end V2 workflow and is designed for early user testing before live data
adapters and AI agents are connected.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping

from stockpilot.v2.domain.models import (
    CompanyProfile,
    Confidence,
    DecisionAction,
    Direction,
    IndustryImpact,
    MarketEvent,
    ResearchAssessment,
    Score,
    TradingDecision,
)
from stockpilot.v2.repositories.sqlite_store import SQLiteResearchRepository


@dataclass(frozen=True, slots=True)
class PipelineResult:
    event: MarketEvent
    industry_impacts: tuple[IndustryImpact, ...]
    assessments: tuple[ResearchAssessment, ...]
    decisions: tuple[TradingDecision, ...]


class EventResearchPipeline:
    """Run one event through industry, company, assessment and decision stages."""

    def __init__(self, repository: SQLiteResearchRepository) -> None:
        self.repository = repository

    def run(
        self,
        event: MarketEvent,
        industry_impacts: Iterable[IndustryImpact],
        *,
        technical_scores: Mapping[str, float] | None = None,
        valuation_scores: Mapping[str, float] | None = None,
        capital_scores: Mapping[str, float] | None = None,
    ) -> PipelineResult:
        technical_scores = technical_scores or {}
        valuation_scores = valuation_scores or {}
        capital_scores = capital_scores or {}

        self.repository.save_event(event)
        impacts = tuple(industry_impacts)
        companies = self.repository.list_company_profiles()
        assessments: list[ResearchAssessment] = []
        decisions: list[TradingDecision] = []

        impact_by_industry = {item.industry_id: item for item in impacts}
        now = datetime.now(timezone.utc)

        for company in companies:
            matching = self._matching_impact(company, impact_by_industry)
            if matching is None:
                continue

            assessment = self._build_assessment(
                company,
                matching,
                now,
                technical_scores=technical_scores,
                valuation_scores=valuation_scores,
                capital_scores=capital_scores,
            )
            decision = self._build_decision(assessment)
            self.repository.save_assessment(assessment)
            self.repository.save_decision(decision)
            assessments.append(assessment)
            decisions.append(decision)

        assessments.sort(key=lambda item: item.total_score.value, reverse=True)
        decision_by_key = {item.asset_id.key: item for item in decisions}
        ordered_decisions = [decision_by_key[item.asset_id.key] for item in assessments]

        return PipelineResult(
            event=event,
            industry_impacts=impacts,
            assessments=tuple(assessments),
            decisions=tuple(ordered_decisions),
        )

    @staticmethod
    def _matching_impact(
        company: CompanyProfile,
        impact_by_industry: Mapping[str, IndustryImpact],
    ) -> IndustryImpact | None:
        candidates = (company.primary_industry_id, *company.industry_ids)
        matches = [impact_by_industry[item] for item in candidates if item in impact_by_industry]
        if not matches:
            return None
        return max(matches, key=lambda item: item.impact_score.value)

    @staticmethod
    def _build_assessment(
        company: CompanyProfile,
        impact: IndustryImpact,
        as_of: datetime,
        *,
        technical_scores: Mapping[str, float],
        valuation_scores: Mapping[str, float],
        capital_scores: Mapping[str, float],
    ) -> ResearchAssessment:
        asset_key = company.asset_id.key
        exposure = max(company.revenue_exposure.values(), default=0.35)
        company_value = min(100.0, 45.0 + exposure * 55.0)
        direction_multiplier = -1.0 if impact.direction == Direction.NEGATIVE else 1.0

        industry_value = impact.impact_score.value
        valuation_value = float(valuation_scores.get(asset_key, 50.0))
        capital_value = float(capital_scores.get(asset_key, 50.0))
        technical_value = float(technical_scores.get(asset_key, 50.0))
        macro_value = 55.0 if impact.direction == Direction.POSITIVE else 45.0

        risk_value = max(
            0.0,
            min(
                100.0,
                50.0
                + max(0.0, technical_value - 85.0) * 0.8
                + max(0.0, 35.0 - valuation_value) * 0.7,
            ),
        )

        raw_total = (
            macro_value * 0.10
            + industry_value * 0.25
            + company_value * 0.25
            + valuation_value * 0.12
            + capital_value * 0.12
            + technical_value * 0.16
            - risk_value * 0.10
        )
        total_value = max(0.0, min(100.0, 50.0 + direction_multiplier * (raw_total - 50.0)))

        confidence = Confidence.HIGH if exposure >= 0.65 else Confidence.MEDIUM
        reasons = (
            f"industry impact={industry_value:.1f}",
            f"revenue exposure={exposure:.0%}",
            f"technical={technical_value:.1f}",
            f"valuation={valuation_value:.1f}",
        )
        return ResearchAssessment(
            asset_id=company.asset_id,
            as_of=as_of,
            macro_score=Score(macro_value, Confidence.MEDIUM),
            industry_score=Score(industry_value, impact.impact_score.confidence, impact.impact_score.reasons),
            company_score=Score(company_value, confidence, ("business exposure derived from company profile",)),
            valuation_score=Score(valuation_value, Confidence.MEDIUM),
            capital_score=Score(capital_value, Confidence.MEDIUM),
            technical_score=Score(technical_value, Confidence.MEDIUM),
            risk_score=Score(risk_value, Confidence.MEDIUM),
            total_score=Score(total_value, confidence, reasons),
            thesis=(
                f"{company.name} matches industry {impact.industry_id}",
                *impact.transmission_path,
            ),
            invalidation_conditions=(
                "event impact is disproved or materially reversed",
                "company business exposure falls below the stored profile",
                "technical trend breaks while industry impact weakens",
            ),
        )

    @staticmethod
    def _build_decision(assessment: ResearchAssessment) -> TradingDecision:
        score = assessment.total_score.value
        risk = assessment.risk_score.value
        technical = assessment.technical_score.value

        if risk >= 75 or score < 45:
            action = DecisionAction.AVOID
            max_weight = 0.0
        elif score >= 82 and technical <= 85 and risk < 60:
            action = DecisionAction.ENTER
            max_weight = 0.12
        elif score >= 72 and technical > 85:
            action = DecisionAction.WAIT_PULLBACK
            max_weight = 0.08
        elif score >= 65:
            action = DecisionAction.WATCH
            max_weight = 0.06
        else:
            action = DecisionAction.AVOID
            max_weight = 0.0

        confidence = assessment.total_score.confidence
        return TradingDecision(
            asset_id=assessment.asset_id,
            as_of=assessment.as_of,
            action=action,
            confidence=confidence,
            assessment=assessment,
            entry_conditions=(
                "industry impact remains valid",
                "price confirms without abnormal volume distribution",
            ),
            exit_conditions=(
                "industry thesis invalidated",
                "risk score rises above 75",
            ),
            max_position_weight=max_weight,
        )
