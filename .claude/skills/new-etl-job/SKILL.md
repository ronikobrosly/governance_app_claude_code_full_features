---
name: new-etl-job
description: >
  Scaffold a new ETL pipeline with all required files: pipeline class,
  Pydantic validation schema, registry entry, job runner integration,
  unit tests, and integration tests. Use this skill whenever the user
  asks to create a new ETL pipeline, add a data ingestion job, build
  a new data feed, or mentions importing data from an external source.
---

# Create a New ETL Pipeline

Follow these steps exactly to create a complete, tested ETL pipeline.

## Step 1: Gather Requirements

Before writing any code, confirm with the user:
- **Source name**: What system/API does data come from? (e.g., "nist_cve_feed")
- **Entity**: What domain object does it produce? (e.g., threats, controls, policies)
- **Source format**: JSON API? CSV file? Message queue?
- **Natural key**: What field(s) make a record unique for upserts?
- **Frequency**: How often will this run? (on-demand, hourly, daily)

## Step 2: Create the Pipeline File

Create `src/etl/{source}_{entity}_pipeline.py` with this structure:

```python
"""ETL pipeline: {Source} → {Entity}."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, field_validator
from src.etl.base import BasePipeline
from src.etl.registry import register_pipeline


class {Entity}Record(BaseModel):
    """Validation schema for incoming {source} records."""
    # Add fields with validators here


class {Source}{Entity}Pipeline(BasePipeline):
    """Ingests {entity} data from {source}."""

    async def extract(self) -> list[dict[str, Any]]:
        ...

    async def validate(self, record: dict[str, Any]) -> dict[str, Any]:
        validated = {Entity}Record(**record)
        return validated.model_dump()

    async def transform(self, records: list[dict[str, Any]]) -> list[Any]:
        ...

    async def load(self, records: list[Any]) -> None:
        # Use ON CONFLICT for idempotent upserts
        ...


register_pipeline("{source}_{entity}", {Source}{Entity}Pipeline)
```

## Step 3: Register the Pipeline

Add an import to `src/etl/__init__.py`:
```python
import src.etl.{source}_{entity}_pipeline  # noqa: F401 (registers pipeline)
```

## Step 4: Write Unit Tests

Create `tests/unit/test_{source}_{entity}_pipeline.py` with:
- `test_pipeline_extract_returns_data` — extract step returns records
- `test_pipeline_validate_accepts_valid_record` — valid record passes
- `test_pipeline_validate_rejects_invalid_{field}` — one per validation rule
- `test_pipeline_full_run_succeeds` — end-to-end run with sample data

## Step 5: Write Integration Test

Add to `tests/integration/test_{source}_{entity}_pipeline.py`:
- Test that `load()` actually writes to the test DB
- Test idempotency: run load twice, verify no duplicates

## Step 6: Verify

Run the checks:
```bash
ruff check src/etl/ tests/ --fix
pytest tests/unit/test_{source}_{entity}_pipeline.py -x -v
```

## Checklist Before Done

- [ ] Pipeline class inherits `BasePipeline`
- [ ] Pydantic model validates all incoming fields
- [ ] `load()` uses upsert (ON CONFLICT)
- [ ] Pipeline registered in `src/etl/registry.py`
- [ ] Unit tests cover happy path + validation errors
- [ ] Integration test verifies DB writes
- [ ] All tests pass
