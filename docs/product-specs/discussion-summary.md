
# Discussion Summary Spec

## Requirement Mapping

- `REQ-FEAT-005`: summarize WG draft discussions for last 3 months.
- `REQ-REL-001`: parser/network failures should return actionable errors.
- `REQ-DATA-001`: deterministic parser with graceful fallback behavior.

## Current Status (Coded, Not Runtime-Verified Here)

- Last-3-month discussion summary is coded.
- Ranked metadata summary includes total posts, frequent topics, active participants, and recent threads.
- Bounded pagination and defensive extraction are coded.

Status:
- `REQ-FEAT-005`: **Coded**.

## Output
- Total posts
- Frequent topics
- Most active participants
- Recent thread list with URLs

## Delivery Surfaces

- CLI option `3`
- MCP tool `draft_discussions_summary(query)`
- Daily pipeline summary helper usage

## Related Tech Debt

- `TD-009`: fixture-backed parser contract tests.
- `TD-010`: pagination depth strategy improvements.
