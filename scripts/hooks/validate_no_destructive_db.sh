#!/usr/bin/env bash
# PreToolUse hook: Block destructive database commands.
# Claude Code passes hook input as JSON via stdin.
# Exit code 0 = allow, exit code 2 = block (feeds error back to Claude).

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

BLOCKED_PATTERNS=(
    "DROP TABLE"
    "DROP DATABASE"
    "TRUNCATE"
    "DELETE FROM.*WHERE 1"
    "DELETE FROM.*--"
    "alembic downgrade base"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -iqE "$pattern"; then
        echo "BLOCKED: Destructive database operation detected: '$pattern'" >&2
        echo "If you need to run this command, do it manually outside Claude Code." >&2
        exit 2
    fi
done

exit 0
