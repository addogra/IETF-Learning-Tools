# Discussion Summary Spec

## Requirement Mapping
- `REQ-FEAT-005`: summarize WG draft discussions for last 3 months.
- `REQ-REL-001`: parser/network failures should return actionable errors.
- `REQ-DATA-001`: deterministic parser with graceful fallback behavior.

## Current Status
- `REQ-FEAT-005`: **Completed** in onboarding slice.
- Output includes:
  - total discussion posts,
  - frequent topics,
  - most active participants,
  - recent discussion threads with URLs.

## Parsing Behavior
- Source: `https://mailarchive.ietf.org/arch/browse/<wg>/`
- Window: 90 days (`get_wg_discussion_summary(..., window_days=90)`).
- Date extraction strategy:
  - prefer explicit `<time>`/`datetime` metadata,
  - use metadata-tagged fallback fields,
  - avoid generic container-date matching that can misread subject deadlines.

## Delivery Surfaces
- CLI option `3` in WG menu.
- MCP tool `draft_discussions_summary(query)`.
- Daily pipeline helper usage for update summaries.

## Related Tech Debt
- `TD-009`: fixture-backed parser contract tests.
- `TD-010`: adaptive pagination depth beyond fixed page bounds.
