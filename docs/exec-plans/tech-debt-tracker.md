
# Tech Debt Tracker

## Open Items
- `TD-001` (High) - Missing technology-onboarding/vector DB lifecycle
  - Requirement refs: `REQ-FEAT-001`, `REQ-MAINT-001..006`, `REQ-VDB-001..003`, `REQ-API-001/002`
  - Gap: no charter corpus build/rebuild, no vector matching pipeline, no technology-input flow.
  - Next action: implement DB lifecycle + deterministic matching API in active plan phase 1.

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
  - Gap: current callable names differ from required API contract names.
  - Next action: add contract-named wrappers/facade and migration notes.

- `TD-008` (Medium) - Maintainer garbage collector missing
  - Requirement refs: `REQ-MAINT-007`
  - Gap: no command for documentation/architecture consistency checks.
  - Next action: implement maintainer command and report format.

- `TD-009` (Medium) - Parser resilience needs fixture-backed contract tests
  - Requirement refs: `REQ-DATA-001`, `REQ-REL-001`
  - Gap: current tests are mostly synthetic HTML snippets; limited captured-fixture regression coverage.
  - Next action: add fixture corpus from real Datatracker/mailarchive pages and parser contract tests.

- `TD-010` (Low) - Mailarchive pagination depth is bounded
  - Requirement refs: `REQ-FEAT-005`, `REQ-DATA-001`
  - Gap: discussion fetchers use fixed `max_pages`; deep thread histories may be under-sampled.
  - Next action: add adaptive pagination stop conditions and coverage for older-page traversal.
