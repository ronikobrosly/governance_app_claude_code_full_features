#!/usr/bin/env bash
# Notification hook: Send a Slack message when Claude Code needs attention.
# Requires SLACK_WEBHOOK_URL environment variable.

set -euo pipefail

INPUT=$(cat)
MESSAGE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message','Claude Code needs your input'))" 2>/dev/null || echo "Claude Code needs your input")

if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
    # No webhook configured — fall back to macOS notification
    if command -v osascript &>/dev/null; then
        osascript -e "display notification \"$MESSAGE\" with title \"Claude Code\""
    fi
    exit 0
fi

curl -s -X POST "$SLACK_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \":robot_face: *Claude Code*: $MESSAGE\"}" \
    >/dev/null 2>&1 || true

exit 0
