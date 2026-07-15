"""Run the first StockPilot V2 end-to-end demo.

Usage:
    python run_v2_demo.py

The demo uses synthetic data so users can verify installation, persistence,
ranking and decisions before real market adapters are enabled.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from stockpilot.v2.domain.models import (
    AssetId,
    CompanyProfile,
    Confidence,
    Direction,
    EventType,
    IndustryImpact,
    IndustryNode,
    Market,
    MarketEvent,
    Score,
)
from stockpilot.v2.pipelines.event_research import EventResearchPipeline
from stockpilot.v2.repositories.sqlite_store import SQLiteResearchRepository


def seed_repository(repository: SQLiteResearchRepository) -> None:
    nodes = (
        IndustryNode("technology", "科技", 1),
        IndustryNode("ai_infrastructure", "AI基础设施", 2, "technology"),
        IndustryNode("optical_module", "光模块", 3, "ai_infrastructure"),
        IndustryNode("pcb", "PCB", 3, "ai_infrastructure"),
    )
    for node in nodes:
        repository.save_industry_node(node)

    companies = (
        CompanyProfile(
            asset_id=AssetId("300308", Market.CN),
            name="示例光模块龙头",
            primary_industry_id="optical_module",
            industry_ids=("ai_infrastructure",),
            products=("高速光模块",),
            revenue_exposure={"optical_module": 0.82},
        ),
        CompanyProfile(
            asset_id=AssetId("002463", Market.CN),
            name="示例PCB公司",
            primary_industry_id="pcb",
            industry_ids=("ai_infrastructure",),
            products=("高速PCB",),
            revenue_exposure={"pcb": 0.58},
        ),
        CompanyProfile(
            asset_id=AssetId("600000", Market.CN),
            name="示例非相关公司",
            primary_industry_id="bank",
            revenue_exposure={"bank": 0.95},
        ),
    )
    for company in companies:
        repository.save_company_profile(company)


def main() -> None:
    database_path = Path("data/demo_stockpilot_v2.db")
    repository = SQLiteResearchRepository(database_path)
    seed_repository(repository)

    event = MarketEvent(
        event_id="demo-ai-capex-001",
        event_type=EventType.INDUSTRY,
        title="示例：全球云厂商提高AI资本开支",
        summary="用于验证事件到行业、公司、评分与交易建议的完整链路。",
        occurred_at=datetime.now(timezone.utc),
        direction=Direction.POSITIVE,
        markets=(Market.GLOBAL, Market.CN),
        entities=("AI服务器", "高速互联"),
        impact_score=Score(
            88,
            Confidence.HIGH,
            ("capital expenditure expansion", "multi-quarter demand visibility"),
        ),
    )
    impacts = (
        IndustryImpact(
            event_id=event.event_id,
            industry_id="optical_module",
            direction=Direction.POSITIVE,
            impact_score=Score(92, Confidence.HIGH, ("direct bandwidth demand",)),
            transmission_path=("AI资本开支", "高速互联", "光模块"),
            horizon_days=180,
        ),
        IndustryImpact(
            event_id=event.event_id,
            industry_id="pcb",
            direction=Direction.POSITIVE,
            impact_score=Score(80, Confidence.MEDIUM, ("server board upgrade",)),
            transmission_path=("AI资本开支", "服务器升级", "高速PCB"),
            horizon_days=180,
        ),
    )

    pipeline = EventResearchPipeline(repository)
    result = pipeline.run(
        event,
        impacts,
        technical_scores={
            "CN:equity:300308": 78,
            "CN:equity:002463": 88,
        },
        valuation_scores={
            "CN:equity:300308": 70,
            "CN:equity:002463": 62,
        },
        capital_scores={
            "CN:equity:300308": 86,
            "CN:equity:002463": 74,
        },
    )

    print("\nStockPilot V2 Demo")
    print("=" * 72)
    print(f"事件：{result.event.title}")
    print(f"数据库：{database_path}")
    print("-" * 72)
    for index, decision in enumerate(result.decisions, start=1):
        assessment = decision.assessment
        profile = repository.get_company_profile(decision.asset_id)
        name = profile.name if profile else decision.asset_id.symbol
        print(
            f"{index}. {name} ({decision.asset_id.symbol}) | "
            f"总分 {assessment.total_score.value:.1f} | "
            f"风险 {assessment.risk_score.value:.1f} | "
            f"建议 {decision.action.value} | "
            f"最大仓位 {decision.max_position_weight:.0%}"
        )
    print("=" * 72)
    print("演示完成：事件、研究评分和交易建议已写入SQLite。")


if __name__ == "__main__":
    main()
