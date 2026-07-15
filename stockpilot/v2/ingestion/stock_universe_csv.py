"""Import an A-share stock universe from CSV into the V2 research store.

The importer is intentionally independent from any single data vendor. It accepts
common Chinese and English column names and converts each row into a CompanyProfile
plus the required IndustryNode records.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from stockpilot.v2.domain.models import AssetId, AssetType, CompanyProfile, IndustryNode, Market
from stockpilot.v2.repositories.sqlite_store import SQLiteResearchRepository


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "symbol": ("证券代码", "股票代码", "代码", "symbol", "code", "ticker"),
    "name": ("证券名称", "股票名称", "名称", "name", "company"),
    "level1": ("一级行业", "申万一级", "行业一级", "industry_l1", "sector"),
    "level2": ("二级行业", "申万二级", "行业二级", "industry_l2", "industry"),
    "level3": ("三级行业", "申万三级", "行业三级", "industry_l3", "subindustry"),
    "products": ("主营产品", "主要产品", "产品", "products"),
    "customers": ("主要客户", "客户", "customers"),
    "competitors": ("竞争对手", "可比公司", "competitors"),
    "themes": ("概念标签", "产业标签", "主题", "themes", "tags"),
}


@dataclass(frozen=True, slots=True)
class ImportSummary:
    rows_read: int
    companies_saved: int
    industries_saved: int
    rows_skipped: int
    warnings: tuple[str, ...] = ()


def import_stock_universe_csv(
    csv_path: str | Path,
    repository: SQLiteResearchRepository,
    *,
    encoding: str | None = None,
) -> ImportSummary:
    """Import company and industry records from a CSV file.

    Required columns are stock code and stock name. Industry columns are optional;
    records without industry information are assigned to ``unclassified`` so they
    remain visible instead of being silently discarded.
    """

    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(path)

    rows_read = 0
    companies_saved = 0
    rows_skipped = 0
    warnings: list[str] = []
    saved_industries: set[str] = set()

    with path.open("r", encoding=encoding or _detect_encoding(path), newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        mapping = _resolve_fields(reader.fieldnames)
        missing = [field for field in ("symbol", "name") if field not in mapping]
        if missing:
            raise ValueError(f"missing required fields: {', '.join(missing)}")

        for line_number, row in enumerate(reader, start=2):
            rows_read += 1
            try:
                symbol = _normalize_symbol(row.get(mapping["symbol"], ""))
                name = str(row.get(mapping["name"], "")).strip()
                if not symbol or not name:
                    raise ValueError("empty stock code or name")

                industry_nodes = _build_industry_nodes(row, mapping)
                if not industry_nodes:
                    industry_nodes = [
                        IndustryNode(
                            node_id="unclassified",
                            name="未分类",
                            level=1,
                            description="Imported company without an industry classification.",
                        )
                    ]

                for node in industry_nodes:
                    if node.node_id not in saved_industries:
                        repository.save_industry_node(node)
                        saved_industries.add(node.node_id)

                profile = CompanyProfile(
                    asset_id=AssetId(symbol=symbol, market=Market.CN, asset_type=AssetType.EQUITY),
                    name=name,
                    primary_industry_id=industry_nodes[-1].node_id,
                    industry_ids=tuple(node.node_id for node in industry_nodes),
                    products=_split_values(_optional(row, mapping, "products")),
                    customers=_split_values(_optional(row, mapping, "customers")),
                    competitors=_split_values(_optional(row, mapping, "competitors")),
                    metadata={
                        "themes": list(_split_values(_optional(row, mapping, "themes"))),
                        "source_file": path.name,
                        "source_line": line_number,
                    },
                )
                repository.save_company_profile(profile)
                companies_saved += 1
            except (TypeError, ValueError) as exc:
                rows_skipped += 1
                warnings.append(f"line {line_number}: {exc}")

    return ImportSummary(
        rows_read=rows_read,
        companies_saved=companies_saved,
        industries_saved=len(saved_industries),
        rows_skipped=rows_skipped,
        warnings=tuple(warnings),
    )


def _resolve_fields(fieldnames: Iterable[str]) -> dict[str, str]:
    normalized = {_normalize_header(name): name for name in fieldnames if name}
    result: dict[str, str] = {}
    for canonical, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            match = normalized.get(_normalize_header(alias))
            if match is not None:
                result[canonical] = match
                break
    return result


def _build_industry_nodes(row: Mapping[str, str], mapping: Mapping[str, str]) -> list[IndustryNode]:
    nodes: list[IndustryNode] = []
    parent_id: str | None = None
    for level, key in enumerate(("level1", "level2", "level3"), start=1):
        value = _optional(row, mapping, key).strip()
        if not value:
            continue
        node_id = _industry_id(parent_id, value)
        nodes.append(
            IndustryNode(
                node_id=node_id,
                name=value,
                level=level,
                parent_id=parent_id,
            )
        )
        parent_id = node_id
    return nodes


def _industry_id(parent_id: str | None, name: str) -> str:
    token = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "-", name.strip().lower()).strip("-")
    return f"{parent_id}/{token}" if parent_id else token


def _optional(row: Mapping[str, str], mapping: Mapping[str, str], key: str) -> str:
    column = mapping.get(key)
    return str(row.get(column, "")) if column else ""


def _split_values(value: str) -> tuple[str, ...]:
    if not value.strip():
        return ()
    parts = re.split(r"[、,，;；|/]+", value)
    return tuple(dict.fromkeys(item.strip() for item in parts if item.strip()))


def _normalize_header(value: str) -> str:
    return re.sub(r"[\s_\-]+", "", value.strip().lower())


def _normalize_symbol(value: object) -> str:
    text = str(value).strip().upper()
    text = re.sub(r"\.(SH|SZ|BJ)$", "", text)
    digits = re.sub(r"\D", "", text)
    if not digits:
        return ""
    return digits.zfill(6)[-6:]


def _detect_encoding(path: Path) -> str:
    sample = path.read_bytes()[:4096]
    for candidate in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            sample.decode(candidate)
            return candidate
        except UnicodeDecodeError:
            continue
    return "gb18030"
