#!/usr/bin/env bash
# Stop hook: Log a summary of what changed in this session.
# Captures the git diff stats and appends to a session log.

set -euo pipefail

LOG_DIR="${HOME}/.claude/session-logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE="${LOG_DIR}/session_$(date +%Y%m%d_%H%M%S).md"

{
    echo "# Claude Code Session — ${TIMESTAMP}"
    echo ""
    echo "## Files Changed"
    git diff --stat HEAD 2>/dev/null || echo "(no git changes detected)"
    echo ""
    echo "## Uncommitted Changes"
    git diff --name-only 2>/dev/null || echo "(none)"
} > "$LOG_FILE"

echo "Session summary written to $LOG_FILE"
exit 0
