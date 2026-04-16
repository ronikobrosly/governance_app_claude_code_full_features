# Testing Conventions

## Unit Tests (`tests/unit/`)
- Test files mirror source structure: `src/services/control_service.py` →
  `tests/unit/test_control_service.py`
- Mock all external dependencies (DB, Redis, HTTP clients) using `unittest.mock`.
- Use `pytest.mark.parametrize` for edge cases.
- Each test function tests ONE behavior. Name format: `test_<method>_<scenario>_<expected>`.
  Example: `test_get_control_missing_id_raises_not_found`

## Integration Tests (`tests/integration/`)
- Use the `test_db` fixture from `conftest.py` — it creates/drops tables per test.
- Test the full request→response cycle via `httpx.AsyncClient`.
- Seed data using factory functions, never raw SQL.
- Mark all with `@pytest.mark.integration` so CI can run them separately.

## Fixtures
- `conftest.py` at `tests/` root has shared fixtures: `test_db`, `async_client`,
  `sample_control`, `sample_threat`, `sample_policy`.
- Don't duplicate fixtures across test files — add to conftest.

## What NOT to Test
- SQLAlchemy model field definitions (tested implicitly via integration tests).
- Third-party library internals.
- Private methods (test via public interface).
