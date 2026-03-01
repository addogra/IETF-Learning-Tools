
# PLANS

## Active Execution Plan

- `docs/exec-plans/active/2026-02-28-requirements-parity-phase-1.md`
  - Focus: remaining high-impact gaps after REQ-FEAT-001..006 + REQ-FEAT-008 completion.
  - Includes: draft-tracker route and delivery-mode parity path.

## Recently Completed

- `docs/exec-plans/completed/2026-02-28-baseline-feature-audit.md`
  - Outcome: code/test audit mapped to requirement coverage and open gaps.
- `docs/exec-plans/completed/2026-02-28-vector-db-maintainer-baseline.md`
  - Outcome: maintainer vector DB lifecycle + contract API baseline + garbage collector command + `/documents/` corpus ingestion.
- `docs/exec-plans/completed/2026-02-28-api-parity-onboarding-gc-hardening.md`
  - Outcome: REQ-API-003..006 wrappers + CLI/MCP technology onboarding + semantic garbage-collector checks.
- `docs/exec-plans/completed/2026-03-01-req-feat-005-iterative-cli.md`
  - Outcome: iterative CLI navigation for REQ-FEAT-001..005 and REQ-FEAT-005 draft-discussion summary option.
- `docs/exec-plans/completed/2026-03-01-req-feat-001-005-docs-sync.md`
  - Outcome: architecture/design/onboarding/tech-debt sync for completed REQ-FEAT-001..005, PlantUML architecture artifact, and parser-date regression notes.
- `docs/exec-plans/completed/2026-03-01-req-feat-006-last-two-ietf-meetings.md`
  - Outcome: CLI option 4, IETF-number meeting filtering, agenda/minutes formatting, tests, and per-feature PlantUML diagrams.
- `docs/exec-plans/completed/2026-03-01-req-feat-008-upcoming-agenda-important-dates.md`
  - Outcome: CLI option 5, important-dates + agenda.txt parsing, required milestone-date output, tests, and PlantUML updates.

## Near-Term Priorities

1. Add draft tracker CLI/MCP user-facing route on top of `track_draft_or_rfc`.
2. Add Webex adapter scaffold for delivery-mode parity.
3. Strengthen parser contract tests with captured fixtures.
4. Add adaptive mailarchive pagination depth controls.
