# WG Summary and Drafts Spec

## Requirement Mapping
- `REQ-FEAT-003`: summary of WG should return complete charter text (non-truncated).
- `REQ-FEAT-004`: active drafts should return active draft identifiers with title and status.

## Current Status
- `REQ-FEAT-003`: **Completed** in onboarding slice.
  - CLI option `1` prints full charter text from `get_wg_charter(...)`.
  - MCP `summary_of_wg(...)` returns full charter text.
- `REQ-FEAT-004`: **Completed** in onboarding slice.
  - CLI option `2` requests latest `10` drafts for performance.
  - Each draft includes at minimum identifier/title/status.

## Data Sources
- WG about page: `https://datatracker.ietf.org/wg/<acronym>/about/`
- WG documents page: `https://datatracker.ietf.org/wg/<acronym>/documents/`
- Draft detail page: `https://datatracker.ietf.org/doc/draft-.../`
- Metadata fallback API: `https://datatracker.ietf.org/api/v1/doc/document/`

## Delivery Surfaces
- CLI option `1`: Summary of WG.
- CLI option `2`: Active drafts.
- MCP tools:
  - `summary_of_wg(query)`
  - `active_drafts(query)`
  - `active_drafts_and_recent_rfcs(query)`

## Notes
- Parser still collects richer metadata (such as abstract/URL) even when CLI displays a minimal set.
- Active-draft count is intentionally capped in onboarding flow to control latency.
