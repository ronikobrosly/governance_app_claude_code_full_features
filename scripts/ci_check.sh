#!/usr/bin/env bash
# CI equivalent check — run this before pushing.
set -euo pipefail

echo "=== Ruff lint ==="
ruff check src/ tests/

echo "=== Mypy type check ==="
mypy src/

echo "=== Unit tests ==="
pytest tests/unit/ -x -q

echo "=== Integration tests ==="
pytest tests/integration/ -x -q --timeout=60

echo ""
echo "✅ All checks passed."
