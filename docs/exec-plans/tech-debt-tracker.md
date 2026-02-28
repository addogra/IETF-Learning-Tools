
# Tech Debt Tracker

## Open Items
- `TD-001` (Medium) - User-facing technology onboarding remains incomplete
  - Requirement refs: `REQ-FEAT-001`, `REQ-MAINT-001..006`, `REQ-VDB-001..003`, `REQ-API-001/002`
  - Progress: maintainer DB lifecycle + local vector matching APIs implemented (`rebuild_wg_charter_db`, `get_db_metadata`, `suggest_wgs_by_technology`).
  - Gap: no CLI/MCP technology-input onboarding flow yet.
  - Next action: wire technology-input route and response formatting across delivery modes.

- `TD-002` (High) - Missing delivery-mode parity for Webex bot
  - Requirement refs: `REQ-MODE-001`, `REQ-MODE-002`
  - Gap: current implementation exposes CLI + MCP + daily scheduler, but no Webex command surface.
  - Next action: add Webex adapter/command mapping with parity tests.

- `TD-003` (High) - Draft tracker not implemented
  - Requirement refs: `REQ-FEAT-010`, `REQ-API-005`
  - Gap: no RFC/draft history timeline tool and no related context aggregation.
  - Next action: add `track_draft_or_rfc` API + CLI/MCP entrypoints.

- `TD-004` (High) - Charter output contract mismatch
  - Requirement refs: `REQ-FEAT-003`
  - Gap: core flows summarize charter text; requirement calls for complete non-truncated charter output.
  - Next action: add explicit full-charter mode and keep summarization as optional view.

- `TD-005` (High) - Last-2-meeting update output lacks summary text
  - Requirement refs: `REQ-FEAT-006`
  - Gap: output currently provides agenda/minutes links without agenda/minutes summaries.
  - Next action: enrich meeting-update model and formatter with short summaries.

- `TD-006` (Medium) - CLI UX contract not fully met
  - Requirement refs: `REQ-INPUT-002`, `REQ-UX-001`
  - Gap: CLI runs one-shot option flow; no iterative follow-up/quit prompt after each action.
  - Next action: introduce looped post-action menu with explicit `Quit`.

- `TD-007` (Medium) - Normative internal API names missing
  - Requirement refs: `REQ-API-001..006`
  - Progress: REQ-API-001/002 names are now present.
  - Gap: REQ-API-003..006 contract names are still missing.
  - Next action: add remaining contract-named wrappers/facade and migration notes.

- `TD-008` (Low) - Garbage collector depth is limited
  - Requirement refs: `REQ-MAINT-007`
  - Progress: `ietf-wg-maintainer garbage-collector` command now exists with artifact/mapping/API checks.
  - Gap: checks do not yet cover deeper semantic drift rules.
  - Next action: expand rule set and severity model for architectural constraints.

- `TD-009` (Medium) - Parser resilience needs fixture-backed contract tests
  - Requirement refs: `REQ-DATA-001`, `REQ-REL-001`
  - Gap: current tests are mostly synthetic HTML snippets; limited captured-fixture regression coverage.
  - Next action: add fixture corpus from real Datatracker/mailarchive pages and parser contract tests.

- `TD-010` (Low) - Mailarchive pagination depth is bounded
  - Requirement refs: `REQ-FEAT-005`, `REQ-DATA-001`
  - Gap: discussion fetchers use fixed `max_pages`; deep thread histories may be under-sampled.
  - Next action: add adaptive pagination stop conditions and coverage for older-page traversal.
