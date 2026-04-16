---
name: add-data-model
description: >
  Add a new SQLAlchemy data model with all associated files: the model class,
  service layer, API router, and tests. Use this skill when the user wants to
  add a new entity, table, domain object, or data type to the platform.
  Also use when they say "we need to track X" or "add a table for Y".
---

# Add a New Data Model

Creates a complete vertical slice: model → service → API → tests.

## Step 1: Define the Model

Create `src/models/{entity}.py`:

```python
"""Model for {Entity}."""
from __future__ import annotations
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class {Entity}(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "{entities}"  # plural, snake_case

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    # ... add fields based on requirements
```

Conventions:
- Always use `UUIDPrimaryKeyMixin` and `TimestampMixin`
- Add `__repr__` for debugging
- Define enums as `str, enum.Enum` subclasses in the same file
- Add relationships with `back_populates` (never `backref`)

## Step 2: Register in `src/models/__init__.py`

Add the import and include in `__all__`.

## Step 3: Create the Service

Create `src/services/{entity}_service.py` with:
- `get_{entity}(session, id) -> {Entity}` — raises NotFoundError
- `list_{entities}(session, **filters) -> list[{Entity}]`
- `create_{entity}(session, **fields) -> {Entity}`

Every method must:
- Accept `AsyncSession` as first arg
- Log entry/exit with structlog
- Raise domain exceptions (never SQLAlchemy exceptions)

## Step 4: Create the API Router

Create `src/api/{entities}.py` with:
- Pydantic `{Entity}Create` and `{Entity}Response` schemas
- `GET /{entities}/` — list with filters
- `GET /{entities}/{id}` — get by ID
- `POST /{entities}/` — create

Register the router in `src/api/__init__.py`.

## Step 5: Write Tests

### Unit tests (`tests/unit/test_{entity}_service.py`):
- `test_get_{entity}_not_found_raises`
- `test_get_{entity}_returns_entity`
- `test_create_{entity}_success`

### Integration tests (`tests/integration/test_{entities}_api.py`):
- `test_create_and_get_{entity}`
- `test_list_{entities}_with_filters`

### Fixture in `tests/conftest.py`:
- Add `sample_{entity}` fixture

## Step 6: Verify

```bash
ruff check src/ tests/
mypy src/
pytest tests/unit/test_{entity}_service.py -x -v
```

## Checklist

- [ ] Model in `src/models/{entity}.py` with mixins
- [ ] Model exported from `src/models/__init__.py`
- [ ] Service in `src/services/{entity}_service.py` with logging
- [ ] API router in `src/api/{entities}.py` with schemas
- [ ] Router registered in `src/api/__init__.py`
- [ ] Unit tests for service layer
- [ ] Integration tests for API endpoints
- [ ] Fixture in `tests/conftest.py`
- [ ] All checks pass
