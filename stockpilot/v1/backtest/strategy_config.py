"""
StockPilot V1.6.3 Strategy Configuration

Defines configurable strategy rules so backtests can be adjusted
without changing core engine logic.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class StrategyConfig:
    name: str
    min_theme_score: float = 80
    allowed_stages: List[str] = field(default_factory=lambda: ["rising", "acceleration"])
    max_risk: str = "medium"
    holding_days: int = 20


MAINLINE_LEADER = StrategyConfig(
    name="mainline_leader",
    min_theme_score=85,
    allowed_stages=["rising", "acceleration"],
    max_risk="medium",
    holding_days=30,
)


DIVERGENCE_ENTRY = StrategyConfig(
    name="divergence_entry",
    min_theme_score=80,
    allowed_stages=["divergence"],
    max_risk="medium",
    holding_days=15,
)


INDUSTRY_CYCLE = StrategyConfig(
    name="industry_cycle",
    min_theme_score=90,
    allowed_stages=["rising", "acceleration"],
    max_risk="low",
    holding_days=60,
)


def get_strategy(name: str) -> StrategyConfig:
    strategies = {
        MAINLINE_LEADER.name: MAINLINE_LEADER,
        DIVERGENCE_ENTRY.name: DIVERGENCE_ENTRY,
        INDUSTRY_CYCLE.name: INDUSTRY_CYCLE,
    }
    return strategies.get(name, MAINLINE_LEADER)
