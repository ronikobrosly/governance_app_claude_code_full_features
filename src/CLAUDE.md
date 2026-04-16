# Source Code Conventions

## Import Order
1. Standard library
2. Third-party packages
3. Local imports (relative within package, absolute across packages)

Separate each group with a blank line. Ruff enforces this via `isort` rules.

## Async Patterns
- All DB operations are async. Use `async with get_session() as session:`.
- Never call `session.commit()` inside a service method. The caller (API layer
  or job runner) owns the transaction boundary.
- Use `asyncio.gather()` for independent concurrent operations, but never for
  DB writes (risk of partial commits).

## Type Hints
- All function signatures must have full type hints.
- Use `typing.Sequence` for read-only collections, `list` for mutable.
- Return `None` explicitly when a function can return nothing.
- Domain IDs are `uuid.UUID`, never `str`.

## Configuration
- All config lives in `src/utils/config.py` via pydantic-settings.
- Environment variables prefixed with `CLOUDGOV_`.
- Never hardcode URLs, credentials, or feature flags.
