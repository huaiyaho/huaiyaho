"""Unified domain models for StockPilot V2.

The V2 platform uses these models as contracts between data ingestion, macro,
event, industry, company, valuation, risk and trading modules.  The models are
stdlib-only so they can be imported by every layer without dependency cycles.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence


class AssetType(str, Enum):
    EQUITY = "equity"
    ETF = "etf"
    CONVERTIBLE_BOND = "convertible_bond"
    REIT = "reit"
    COMMODITY = "commodity"
    FX = "fx"
    CRYPTO = "crypto"


class Market(str, Enum):
    CN = "CN"
    HK = "HK"
    US = "US"
    GLOBAL = "GLOBAL"


class EventType(str, Enum):
    MACRO = "macro"
    POLICY = "policy"
    EARNINGS = "earnings"
    CORPORATE = "corporate"
    INDUSTRY = "industry"
    COMMODITY = "commodity"
    GEOPOLITICAL = "geopolitical"
    WEATHER = "weather"
    OTHER = "other"


class Direction(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    MIXED = "mixed"
    NEUTRAL = "neutral"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionAction(str, Enum):
    AVOID = "avoid"
    WATCH = "watch"
    WAIT_PULLBACK = "wait_pullback"
    ENTER = "enter"
    HOLD = "hold"
    REDUCE = "reduce"
    EXIT = "exit"


@dataclass(frozen=True, slots=True)
class AssetId:
    symbol: str
    market: Market
    asset_type: AssetType = AssetType.EQUITY

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        if not symbol:
            raise ValueError("symbol must not be empty")
        object.__setattr__(self, "symbol", symbol)

    @property
    def key(self) -> str:
        return f"{self.market.value}:{self.asset_type.value}:{self.symbol}"


@dataclass(frozen=True, slots=True)
class SourceRef:
    source_id: str
    title: str
    url: str | None = None
    published_at: datetime | None = None
    retrieved_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True, slots=True)
class Score:
    value: float
    confidence: Confidence = Confidence.MEDIUM
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 100:
            raise ValueError("score value must be between 0 and 100")


@dataclass(frozen=True, slots=True)
class MarketEvent:
    event_id: str
    event_type: EventType
    title: str
    summary: str
    occurred_at: datetime
    direction: Direction = Direction.NEUTRAL
    markets: tuple[Market, ...] = (Market.GLOBAL,)
    entities: tuple[str, ...] = ()
    source_refs: tuple[SourceRef, ...] = ()
    impact_score: Score | None = None
    raw_payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class IndustryNode:
    node_id: str
    name: str
    level: int
    parent_id: str | None = None
    aliases: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self) -> None:
        if self.level < 1:
            raise ValueError("industry level must be >= 1")


@dataclass(frozen=True, slots=True)
class IndustryImpact:
    event_id: str
    industry_id: str
    direction: Direction
    impact_score: Score
    transmission_path: tuple[str, ...]
    horizon_days: int | None = None


@dataclass(frozen=True, slots=True)
class CompanyProfile:
    asset_id: AssetId
    name: str
    primary_industry_id: str
    industry_ids: tuple[str, ...] = ()
    products: tuple[str, ...] = ()
    customers: tuple[str, ...] = ()
    competitors: tuple[str, ...] = ()
    revenue_exposure: Mapping[str, float] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for label, value in self.revenue_exposure.items():
            if not 0 <= value <= 1:
                raise ValueError(
                    f"revenue exposure for {label!r} must be between 0 and 1"
                )


@dataclass(frozen=True, slots=True)
class CompanyImpact:
    event_id: str
    asset_id: AssetId
    industry_id: str
    direction: Direction
    purity_score: Score
    earnings_elasticity_score: Score
    beneficiary_score: Score
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FundamentalSnapshot:
    asset_id: AssetId
    as_of: date
    revenue: float | None = None
    net_profit: float | None = None
    gross_margin: float | None = None
    roe: float | None = None
    operating_cash_flow: float | None = None
    revenue_growth: float | None = None
    profit_growth: float | None = None
    currency: str = "CNY"
    source_refs: tuple[SourceRef, ...] = ()


@dataclass(frozen=True, slots=True)
class ValuationSnapshot:
    asset_id: AssetId
    as_of: date
    pe_ttm: float | None = None
    pb: float | None = None
    ps_ttm: float | None = None
    ev_ebitda: float | None = None
    historical_percentile: float | None = None

    def __post_init__(self) -> None:
        percentile = self.historical_percentile
        if percentile is not None and not 0 <= percentile <= 1:
            raise ValueError("historical_percentile must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class TechnicalSnapshot:
    asset_id: AssetId
    as_of: datetime
    close: float
    trend_score: Score
    momentum_score: Score
    liquidity_score: Score
    position_score: Score
    risk_flags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ResearchAssessment:
    asset_id: AssetId
    as_of: datetime
    macro_score: Score
    industry_score: Score
    company_score: Score
    valuation_score: Score
    capital_score: Score
    technical_score: Score
    risk_score: Score
    total_score: Score
    thesis: tuple[str, ...] = ()
    invalidation_conditions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TradingDecision:
    asset_id: AssetId
    as_of: datetime
    action: DecisionAction
    confidence: Confidence
    assessment: ResearchAssessment
    entry_conditions: tuple[str, ...] = ()
    exit_conditions: tuple[str, ...] = ()
    max_position_weight: float | None = None

    def __post_init__(self) -> None:
        weight = self.max_position_weight
        if weight is not None and not 0 <= weight <= 1:
            raise ValueError("max_position_weight must be between 0 and 1")


def to_dict(model: Any) -> dict[str, Any]:
    """Serialize a domain dataclass into a JSON-friendly dictionary."""

    def normalize(value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Mapping):
            return {str(k): normalize(v) for k, v in value.items()}
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return [normalize(item) for item in value]
        return value

    return normalize(asdict(model))
