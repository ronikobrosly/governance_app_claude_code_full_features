# CloudGov Platform — Backend

## Philosophy
This platform manages **cloud service controls**, a **threat registry**, and **governance data**
for internal compliance teams. Reliability, auditability, and correctness are paramount.
Every mutation must be logged. Every ETL pipeline must be idempotent. Every API response
must include tracing headers.

## Tech Stack
- Python 3.12, FastAPI, SQLAlchemy 2.x (async), Alembic
- PostgreSQL 16 (primary), Redis (caching/queues)
- Pytest + pytest-asyncio for testing
- Ruff for linting, mypy for type checking

## Repository Layout
```
src/
├── api/           # FastAPI routers and request/response schemas
├── models/        # SQLAlchemy ORM models (one file per domain entity)
├── services/      # Business logic layer (never import FastAPI here)
├── etl/           # Extract-Transform-Load pipelines
├── jobs/          # Scheduled and on-demand job definitions
├── db/            # Database session, migrations, connection helpers
└── utils/         # Shared utilities: logging, tracing, config
tests/
├── unit/          # Fast, no-DB tests (mock everything external)
└── integration/   # Requires test DB, runs in CI
```

## Starting the Service

The FastAPI app is defined via a factory function in src/api/__init__.py:10. There's no dedicated main.py, so you run it with uvicorn pointing at the factory:

```bash
uvicorn "src.api:create_app" --factory --host 0.0.0.0 --port 8000

# Or for development with auto-reload:

uvicorn "src.api:create_app" --factory --reload
```

The app exposes:
- GET /health — health check
- GET|POST /api/v1/... — controls router (from src/api/controls.py)
- GET /docs — Swagger UI


## Commands — Run These to Validate Changes
```bash
# Lint + type check
ruff check src/ tests/ && mypy src/

# Unit tests (fast, no DB)
pytest tests/unit/ -x -q

# Integration tests (requires TEST_DATABASE_URL)
pytest tests/integration/ -x -q

# All checks (CI equivalent)
./scripts/ci_check.sh
```

## Key Conventions
- **Logging**: Use `structlog` via `src/utils/logging.py`. Every service method
  logs entry/exit with correlation IDs. Never use `print()`.
- **Error handling**: Raise domain exceptions from `src/utils/exceptions.py`.
  API layer catches and maps to HTTP status codes.
- **Testing**: Every service method needs ≥1 unit test. Every API endpoint needs
  ≥1 integration test. Use factories from `tests/conftest.py`.
- **Imports**: Services import models, never the reverse. API imports services,
  never models directly. ETL may import both.
- **Naming**: snake_case everywhere. Files named after the domain entity they own.
  e.g. `models/control.py`, `services/control_service.py`.

## ETL Pipeline Pattern
All ETL jobs follow this pattern:
1. Extract: Pull from source (API, file, queue) into raw dicts
2. Validate: Pydantic model validates each record
3. Transform: Map to internal domain model
4. Load: Upsert to DB (idempotent via natural keys)
5. Audit: Write job run record to `etl_job_runs` table

## Business Logic Notes
- **Controls** belong to **Services** (1:many). A Control has a `status` enum:
  `draft`, `active`, `deprecated`, `archived`.
- **Threats** are independent entities linked to Controls via `threat_control_mappings`.
- **Governance Policies** are versioned. The `effective_date` determines which version
  is active. Never delete old versions — set `superseded_by`.
- **Risk scores** are computed, never stored. See `services/risk_service.py`.
