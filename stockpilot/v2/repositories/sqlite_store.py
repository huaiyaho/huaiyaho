"""SQLite persistence for StockPilot V2 domain models.

The repository deliberately stores complete domain objects as versioned JSON while
also exposing indexed columns for the fields used by daily research workflows.
This keeps the schema stable while the V2 models continue to evolve.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any, Iterable, Iterator, Mapping, TypeVar, Union, get_args, get_origin, get_type_hints

from stockpilot.v2.domain.models import (
    AssetId,
    CompanyProfile,
    IndustryNode,
    MarketEvent,
    ResearchAssessment,
    TradingDecision,
    to_dict,
)

T = TypeVar("T")
SCHEMA_VERSION = 1


class RepositoryError(RuntimeError):
    """Raised when persisted data cannot be read or written safely."""


class SQLiteResearchRepository:
    """Persistent V2 research store backed by SQLite.

    The class is safe for repeated CLI invocations. Each public write method uses
    its own transaction and performs an upsert, making the operation idempotent.
    """

    def __init__(self, database_path: str | Path = "data/stockpilot_v2.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS repository_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS market_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    title TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_events_occurred_at
                    ON market_events(occurred_at DESC);
                CREATE INDEX IF NOT EXISTS idx_events_type
                    ON market_events(event_type, occurred_at DESC);

                CREATE TABLE IF NOT EXISTS industry_nodes (
                    node_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    parent_id TEXT,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_industry_parent
                    ON industry_nodes(parent_id, level);

                CREATE TABLE IF NOT EXISTS company_profiles (
                    asset_key TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    market TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    primary_industry_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_company_industry
                    ON company_profiles(primary_industry_id, market);

                CREATE TABLE IF NOT EXISTS research_assessments (
                    asset_key TEXT NOT NULL,
                    as_of TEXT NOT NULL,
                    total_score REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(asset_key, as_of)
                );
                CREATE INDEX IF NOT EXISTS idx_assessment_latest
                    ON research_assessments(as_of DESC, total_score DESC);

                CREATE TABLE IF NOT EXISTS trading_decisions (
                    asset_key TEXT NOT NULL,
                    as_of TEXT NOT NULL,
                    action TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    max_position_weight REAL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(asset_key, as_of)
                );
                CREATE INDEX IF NOT EXISTS idx_decision_latest
                    ON trading_decisions(as_of DESC, action);
                """
            )
            connection.execute(
                """
                INSERT INTO repository_meta(key, value) VALUES('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(SCHEMA_VERSION),),
            )

    def save_event(self, event: MarketEvent) -> None:
        payload = _encode(event)
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO market_events(
                    event_id, event_type, occurred_at, direction, title,
                    payload_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(event_id) DO UPDATE SET
                    event_type = excluded.event_type,
                    occurred_at = excluded.occurred_at,
                    direction = excluded.direction,
                    title = excluded.title,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (
                    event.event_id,
                    event.event_type.value,
                    event.occurred_at.isoformat(),
                    event.direction.value,
                    event.title,
                    payload,
                    _utc_now(),
                ),
            )

    def get_event(self, event_id: str) -> MarketEvent | None:
        payload = self._fetch_payload(
            "SELECT payload_json FROM market_events WHERE event_id = ?", (event_id,)
        )
        return _decode(MarketEvent, payload) if payload else None

    def list_events(self, *, limit: int = 100) -> list[MarketEvent]:
        return self._list_models(
            MarketEvent,
            "SELECT payload_json FROM market_events ORDER BY occurred_at DESC LIMIT ?",
            (self._validate_limit(limit),),
        )

    def save_industry_node(self, node: IndustryNode) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO industry_nodes(
                    node_id, name, level, parent_id, payload_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    name = excluded.name,
                    level = excluded.level,
                    parent_id = excluded.parent_id,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (
                    node.node_id,
                    node.name,
                    node.level,
                    node.parent_id,
                    _encode(node),
                    _utc_now(),
                ),
            )

    def list_industry_nodes(self) -> list[IndustryNode]:
        return self._list_models(
            IndustryNode,
            "SELECT payload_json FROM industry_nodes ORDER BY level, name",
        )

    def save_company_profile(self, profile: CompanyProfile) -> None:
        asset = profile.asset_id
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO company_profiles(
                    asset_key, symbol, market, asset_type, name,
                    primary_industry_id, payload_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asset_key) DO UPDATE SET
                    symbol = excluded.symbol,
                    market = excluded.market,
                    asset_type = excluded.asset_type,
                    name = excluded.name,
                    primary_industry_id = excluded.primary_industry_id,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (
                    asset.key,
                    asset.symbol,
                    asset.market.value,
                    asset.asset_type.value,
                    profile.name,
                    profile.primary_industry_id,
                    _encode(profile),
                    _utc_now(),
                ),
            )

    def get_company_profile(self, asset_id: AssetId) -> CompanyProfile | None:
        payload = self._fetch_payload(
            "SELECT payload_json FROM company_profiles WHERE asset_key = ?",
            (asset_id.key,),
        )
        return _decode(CompanyProfile, payload) if payload else None

    def list_company_profiles(
        self,
        *,
        primary_industry_id: str | None = None,
        limit: int = 5000,
    ) -> list[CompanyProfile]:
        if primary_industry_id:
            sql = (
                "SELECT payload_json FROM company_profiles "
                "WHERE primary_industry_id = ? ORDER BY name LIMIT ?"
            )
            params: tuple[Any, ...] = (
                primary_industry_id,
                self._validate_limit(limit),
            )
        else:
            sql = "SELECT payload_json FROM company_profiles ORDER BY name LIMIT ?"
            params = (self._validate_limit(limit),)
        return self._list_models(CompanyProfile, sql, params)

    def save_assessment(self, assessment: ResearchAssessment) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO research_assessments(
                    asset_key, as_of, total_score, risk_score,
                    payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(asset_key, as_of) DO UPDATE SET
                    total_score = excluded.total_score,
                    risk_score = excluded.risk_score,
                    payload_json = excluded.payload_json,
                    created_at = excluded.created_at
                """,
                (
                    assessment.asset_id.key,
                    assessment.as_of.isoformat(),
                    assessment.total_score.value,
                    assessment.risk_score.value,
                    _encode(assessment),
                    _utc_now(),
                ),
            )

    def latest_assessments(self, *, limit: int = 100) -> list[ResearchAssessment]:
        return self._list_models(
            ResearchAssessment,
            """
            SELECT payload_json FROM research_assessments
            WHERE as_of = (SELECT MAX(as_of) FROM research_assessments)
            ORDER BY total_score DESC LIMIT ?
            """,
            (self._validate_limit(limit),),
        )

    def save_decision(self, decision: TradingDecision) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO trading_decisions(
                    asset_key, as_of, action, confidence, max_position_weight,
                    payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asset_key, as_of) DO UPDATE SET
                    action = excluded.action,
                    confidence = excluded.confidence,
                    max_position_weight = excluded.max_position_weight,
                    payload_json = excluded.payload_json,
                    created_at = excluded.created_at
                """,
                (
                    decision.asset_id.key,
                    decision.as_of.isoformat(),
                    decision.action.value,
                    decision.confidence.value,
                    decision.max_position_weight,
                    _encode(decision),
                    _utc_now(),
                ),
            )

    def latest_decisions(self, *, limit: int = 100) -> list[TradingDecision]:
        return self._list_models(
            TradingDecision,
            """
            SELECT payload_json FROM trading_decisions
            WHERE as_of = (SELECT MAX(as_of) FROM trading_decisions)
            ORDER BY asset_key LIMIT ?
            """,
            (self._validate_limit(limit),),
        )

    def _fetch_payload(self, sql: str, params: tuple[Any, ...]) -> str | None:
        with self.connection() as connection:
            row = connection.execute(sql, params).fetchone()
        return str(row["payload_json"]) if row else None

    def _list_models(
        self,
        model_type: type[T],
        sql: str,
        params: tuple[Any, ...] = (),
    ) -> list[T]:
        with self.connection() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [_decode(model_type, str(row["payload_json"])) for row in rows]

    @staticmethod
    def _validate_limit(limit: int) -> int:
        if limit < 1 or limit > 100_000:
            raise ValueError("limit must be between 1 and 100000")
        return limit


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _encode(model: Any) -> str:
    return json.dumps(
        {"schema_version": SCHEMA_VERSION, "data": to_dict(model)},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _decode(model_type: type[T], payload_json: str) -> T:
    try:
        envelope = json.loads(payload_json)
        if envelope.get("schema_version") != SCHEMA_VERSION:
            raise RepositoryError(
                f"unsupported schema version: {envelope.get('schema_version')}"
            )
        return _construct(model_type, envelope["data"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RepositoryError(f"failed to decode {model_type.__name__}") from exc


def _construct(target_type: Any, value: Any) -> Any:
    if value is None:
        return None

    origin = get_origin(target_type)
    args = get_args(target_type)

    if origin in (Union, UnionType):
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1:
            return _construct(non_none[0], value)

    if origin in (tuple, list, set, frozenset):
        item_type = args[0] if args else Any
        items = [_construct(item_type, item) for item in value]
        return origin(items) if origin is not tuple else tuple(items)

    if origin in (dict, Mapping):
        key_type, item_type = args if len(args) == 2 else (str, Any)
        return {
            _construct(key_type, key): _construct(item_type, item)
            for key, item in value.items()
        }

    if target_type is Any:
        return value
    if target_type is datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    if target_type is date:
        return date.fromisoformat(value)
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        return target_type(value)
    if isinstance(target_type, type) and is_dataclass(target_type):
        hints = get_type_hints(target_type)
        kwargs = {
            field.name: _construct(hints.get(field.name, Any), value[field.name])
            for field in fields(target_type)
            if field.name in value
        }
        return target_type(**kwargs)
    return value
