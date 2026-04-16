---
description: >
  Research a problem using web search, documentation, and codebase
  exploration in parallel. Produces a structured research report.
allowed-tools:
  - Task
  - WebSearch
  - WebFetch
  - Grep
  - Glob
  - Read
  - Write
  - Bash
---

# Research: $ARGUMENTS

Research the following topic thoroughly:

> **$ARGUMENTS**

## Instructions

Launch multiple subagents **in parallel** to gather information fast.

### Step 1: Spawn Parallel Research Agents

Use the Task tool to spawn these subagents **in a single message**:

1. **Web Documentation Agent** (subagent_type: general-purpose)
   - Search official docs for the topic
   - Find best practices and recommended patterns
   - Locate relevant GitHub issues or discussions

2. **Codebase Explorer Agent** (subagent_type: explorer)
   - Search the codebase for related patterns
   - Find existing solutions to similar problems
   - Identify relevant files and functions

3. **Stack Overflow / Community Agent** (subagent_type: general-purpose)
   - Search for community solutions and common pitfalls
   - Find highly-voted answers
   - Note gotchas and anti-patterns

### Step 2: Synthesize Findings

After all agents complete, create a markdown file at
`docs/research/$ARGUMENTS.md` (slugified).

Structure the document:
```markdown
# Research: [Topic]
**Date:** YYYY-MM-DD

## Summary
2-3 sentence overview

## Key Findings
Most relevant solutions and approaches

## Codebase Patterns
How our codebase currently handles related concerns

## Community Solutions
What others have done

## Recommendation
The recommended approach for our project and why
```

### Step 3: Present

Share the research doc and give a brief verbal summary.
