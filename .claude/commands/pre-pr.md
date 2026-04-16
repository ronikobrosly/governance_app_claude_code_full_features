---
description: >
  Run a comprehensive pre-PR review: lint, type check, tests,
  security scan, and generate a PR description. Use before
  pushing a branch.
allowed-tools:
  - Task
  - Bash
  - Read
  - Grep
  - View
  - Write
---

# Pre-PR Review

Run all checks and prepare a PR for the current branch.

## Step 1: Run Quality Checks

```bash
ruff check src/ tests/ --fix
mypy src/
pytest tests/unit/ -x -q
pytest tests/integration/ -x -q
```

If any step fails, fix the issue before continuing.

## Step 2: Security Review (parallel subagent)

Spawn the `security-reviewer` agent to audit the current diff:

> Review the changes in `git diff main...HEAD` for security issues.

## Step 3: Generate PR Description

Based on the diff, create a PR description:

```markdown
## What Changed
[Bullet list of changes]

## Why
[Motivation / ticket reference]

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Lint clean
- [ ] Type check clean
- [ ] Security review: [PASS/FLAGS]

## Screenshots / Examples
[If applicable]
```

## Step 4: Report

Present the PR description and any issues found.
