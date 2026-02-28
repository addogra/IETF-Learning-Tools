
# WG Summary and Drafts Spec

## Requirement Mapping

- `REQ-FEAT-003`: summary of WG should return complete charter text (non-truncated).
- `REQ-FEAT-004`: active drafts should return latest 5 drafts with title, status, abstract.

## Current Status (Coded, Not Runtime-Verified Here)

- WG charter fetch is coded.
- Current CLI/MCP default renders summarized charter view.
- Active drafts extraction (top 5, status, abstract, URL) is coded with API + HTML fallback parsing.

Status:
- `REQ-FEAT-003`: **Partially coded** (full non-truncated charter output mode is tracked gap).
- `REQ-FEAT-004`: **Coded**.

## Data Sources

- WG about page: `https://datatracker.ietf.org/wg/<acronym>/about/`
- WG documents page: `https://datatracker.ietf.org/wg/<acronym>/documents/`
- Draft detail page: `https://datatracker.ietf.org/doc/draft-.../`
- Optional metadata fallback API: `https://datatracker.ietf.org/api/v1/doc/document/`

## Delivery Surfaces

- CLI option `1` (summary of WG)
- CLI option `2` (active drafts)
- MCP tools:
  - `summary_of_wg(query)`
  - `active_drafts(query)`
  - `active_drafts_and_recent_rfcs(query)`

## Related Tech Debt

- `TD-004`: full charter output contract mismatch.
