# Tech Debt Tracker

## Open Items
- `TD-002` (High) - Missing delivery-mode parity for Webex bot
  - Requirement refs: `REQ-MODE-001`, `REQ-MODE-002`
  - Gap: current implementation exposes CLI + MCP + daily scheduler, but no Webex command surface.
  - Next action: add Webex adapter/command mapping with parity tests.

- `TD-003` (Medium) - Draft tracker user-facing route is incomplete
  - Requirement refs: `REQ-FEAT-010`, `REQ-API-005`
  - Progress: `track_draft_or_rfc(identifier, include_vendor_signals=False)` API wrapper is implemented.
  - Gap: no dedicated CLI/MCP command path for draft tracking and timeline rendering yet.
  - Next action: add CLI/MCP surfaces for draft tracker output formatting.

- `TD-005` (High) - Last-2-meeting update output lacks summary text
  - Requirement refs: `REQ-FEAT-006`
  - Gap: output currently provides agenda/minutes links without agenda/minutes summaries.
  - Next action: enrich meeting-update model and formatter with short summaries.

- `TD-008` (Low) - Garbage collector depth is limited
  - Requirement refs: `REQ-MAINT-007`
  - Progress: garbage collector includes semantic checks (API-doc alignment, entrypoint alignment, module-index alignment, schema token checks).
  - Gap: dynamic runtime invariants and deeper architectural rules are not yet enforced.
  - Next action: add runtime-oriented semantic checks and severity classes.

- `TD-009` (Medium) - Parser resilience needs fixture-backed contract tests
  - Requirement refs: `REQ-DATA-001`, `REQ-REL-001`
  - Gap: current tests are mostly synthetic HTML snippets; limited captured-fixture regression coverage.
  - Next action: add fixture corpus from real Datatracker/mailarchive pages and parser contract tests.

- `TD-010` (Low) - Mailarchive pagination depth is bounded
  - Requirement refs: `REQ-FEAT-005`, `REQ-DATA-001`
  - Gap: discussion fetchers use fixed `max_pages`; deep thread histories may be under-sampled.
  - Next action: add adaptive pagination stop conditions and coverage for older-page traversal.

- `TD-011` (Low) - Technology onboarding output UX cleanup (hide score in user view)
  - Requirement refs: `REQ-FEAT-001`, `REQ-UX-003`
  - Progress: onboarding output currently shows ranking score and matched-term explanation for debugging.
  - Gap: user-facing output should prioritize clean WG recommendations without raw score noise.
  - Next action: add a presentation mode that suppresses numeric score in default user output while keeping a debug mode.

## Recently Closed
- `TD-001` - Technology onboarding integration baseline
  - Closed by CLI + MCP onboarding routes powered by `suggest_wgs_by_technology(...)`.

- `TD-004` - Full charter output contract mismatch
  - Closed by complete charter output in both CLI and MCP `summary_of_wg(...)` path.

- `TD-006` - Iterative CLI UX contract
  - Closed for REQ-FEAT-001..005 slice with stable `Back`/`Quit` navigation and prompt cleanup.
