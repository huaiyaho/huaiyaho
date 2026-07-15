# StockPilot V2 Architecture

## Purpose

StockPilot V2 is a research platform, not a collection of isolated scoring scripts.
Every module communicates through the unified domain models in
`stockpilot/v2/domain/models.py`.

## Processing flow

```text
Sources
  -> ingestion and provenance
  -> normalized events and market observations
  -> macro and industry transmission analysis
  -> company exposure and fundamental analysis
  -> valuation, capital, technical and risk assessment
  -> research assessment
  -> trading decision
  -> history, evaluation and strategy lab
```

## Architectural layers

### 1. Domain layer

Owns stable business objects and validation rules:

- assets and markets
- sources and events
- industries and transmission paths
- companies and business exposure
- fundamentals and valuation
- technical observations
- research assessments
- trading decisions

The domain layer must remain independent of data vendors, databases and web
frameworks.

### 2. Data and provenance layer

Responsibilities:

- connect CSV, XLSX, market APIs, filings and news feeds
- preserve source identity, publication time and retrieval time
- normalize symbols, units, currencies and timestamps
- reject incomplete or contradictory records
- make every conclusion traceable to its supporting sources

### 3. Knowledge graph layer

Canonical relationships:

```text
Event -> Industry -> Product -> Company -> Customer -> Competitor
```

Relationships must carry direction, confidence, effective dates and evidence.
The initial implementation may use SQLite tables; graph storage is an optional
future optimization, not a prerequisite.

### 4. Research engines

Independent engines consume domain objects and emit scored evidence:

- Macro Engine
- Event Engine
- Industry Engine
- Company Engine
- Valuation Engine
- Capital Engine
- Technical Engine
- Risk Engine

No engine may directly produce a final buy or sell instruction.

### 5. CIO aggregation layer

The CIO layer combines engine outputs into one `ResearchAssessment`.
Weights are configuration and strategy specific. Missing evidence reduces
confidence instead of silently becoming a neutral score.

### 6. Trading layer

The Trading Engine converts a validated assessment into a `TradingDecision`.
It must specify:

- action
- confidence
- entry conditions
- exit or invalidation conditions
- maximum position weight

Order execution is explicitly outside the platform boundary.

### 7. Strategy Lab

The Strategy Lab replays point-in-time data and evaluates decisions with:

- total and annualized return
- maximum drawdown
- win rate and payoff ratio
- turnover and holding period
- regime and industry attribution
- data leakage checks

## Non-negotiable rules

1. Point-in-time correctness: a historical run may only use information known at
   that time.
2. Provenance: material conclusions require source references.
3. Separation of concerns: data adapters cannot contain investment logic.
4. Missing-data honesty: unavailable data must remain unavailable, not invented.
5. Full-industry coverage: user interests influence views and alerts, not the
   boundaries of the industry universe.
6. No automated brokerage execution in V2.

## Migration from V1

V1 modules remain usable while they are migrated behind V2 interfaces.
Migration order:

1. Wrap existing data adapters to emit V2 domain objects.
2. Replace ad-hoc event dictionaries with `MarketEvent`.
3. Replace company and industry dictionaries with graph-backed records.
4. Make scoring engines emit `Score` objects with reasons and confidence.
5. Aggregate outputs into `ResearchAssessment`.
6. Make Dashboard and reports read assessments and decisions only.
7. Retire duplicate V1 scoring paths after regression tests pass.

## Immediate implementation sequence

1. Domain models and serialization.
2. SQLite repository interfaces for events, industries, companies and snapshots.
3. Industry taxonomy importer covering the full market.
4. Source/provenance-aware event ingestion.
5. First end-to-end vertical slice:
   event -> industry impact -> company impact -> assessment -> dashboard.
6. Point-in-time tests and a reproducible demo dataset.
