---
name: refactor-module
description: >
  Safely refactor a Python module in the CloudGov codebase. Use this skill
  whenever the user asks to refactor, restructure, reorganize, clean up,
  or improve the architecture of existing code. Also use when splitting
  a file into smaller modules, extracting shared logic, or renaming things
  across the codebase.
---

# Safe Module Refactoring

Refactoring in this codebase requires care because of extensive cross-module
imports, structured logging, and test coverage requirements.

## Phase 1: Impact Analysis (use the explorer subagent)

Before changing anything, spawn the `explorer` agent to produce an impact report:

> Use the explorer agent to find every file that imports from `{target_module}`
> and every test that exercises its public functions.

Wait for the report before proceeding.

## Phase 2: Plan the Refactor

Write a brief plan as a markdown checklist covering:
- [ ] What's changing and why
- [ ] Files being modified
- [ ] Files being created or deleted
- [ ] Import paths that will change
- [ ] Tests that need updating

Share the plan with the user for approval before proceeding.

## Phase 3: Execute Changes

Apply changes in this order to keep tests green at each step:

1. **Create new structure** (new files/modules) without deleting old ones
2. **Move logic** to new locations, keeping old locations as re-exports
3. **Update imports** across the codebase to point to new locations
4. **Run tests** — everything should still pass at this point
5. **Remove old re-exports** once all imports are updated
6. **Run tests again** — confirm nothing broke
7. **Update CLAUDE.md** files if the folder structure description changed

## Phase 4: Verify

```bash
# Full validation
ruff check src/ tests/ --fix
mypy src/
pytest tests/unit/ -x -q
pytest tests/integration/ -x -q
```

## Phase 5: Test Coverage (use the test-writer subagent)

> Use the test-writer agent to check if any new code paths are untested
> and add tests as needed.

## Rules

- NEVER delete a module and recreate it in one step — always do move-then-delete
- NEVER change function signatures without updating all callers first
- ALWAYS keep tests passing between each step
- ALWAYS update the logging context (logger name) when moving functions
- If a refactor touches more than 10 files, break it into smaller PRs
