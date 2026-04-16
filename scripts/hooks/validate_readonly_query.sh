#!/usr/bin/env bash
# PreToolUse hook for the db-reader subagent.
# Only allows SELECT, EXPLAIN, and describe commands.
# Exit 0 = allow, exit 2 = block.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

# Allow empty commands (non-Bash tools)
if [ -z "$COMMAND" ]; then
    exit 0
fi

# Normalize to uppercase for matching
UPPER_CMD=$(echo "$COMMAND" | tr '[:lower:]' '[:upper:]')

# Block write operations
WRITE_PATTERNS=(
    "INSERT"
    "UPDATE"
    "DELETE"
    "DROP"
    "TRUNCATE"
    "ALTER"
    "CREATE TABLE"
    "CREATE INDEX"
    "GRANT"
    "REVOKE"
)

for pattern in "${WRITE_PATTERNS[@]}"; do
    if echo "$UPPER_CMD" | grep -qw "$pattern"; then
        echo "BLOCKED: Write operation '$pattern' not allowed in read-only mode." >&2
        exit 2
    fi
done

exit 0
