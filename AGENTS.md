
# AGENTS.md

## Mission
Build and maintain an IETF WG assistant that reliably resolves WG names, maps technology-to-WG intent, summarizes charter/discussions/meetings, tracks drafts, and supports scheduled updates across delivery modes.

## Startup Context Bootstrap (Mandatory For Every New Agent Session)
Before proposing or writing changes, traverse these files in this exact order:
1. `requirements.txt`
2. `ARCHITECTURE.md`
3. `docs/product-specs/new-user-onboarding.md`
4. `docs/design-docs/index.md`
5. `docs/design-docs/internal-api-contract.md`
6. `docs/exec-plans/active/README.md`
7. `docs/exec-plans/active/` (current active plan file)
8. `docs/exec-plans/tech-debt-tracker.md`
9. `Lessons.md`
10. `coding_practices.md`

Do not start implementation until the above context is loaded and the impacted requirement IDs are identified.

## Current Product Context Snapshot
- Onboarding slice `REQ-FEAT-001..005` is implemented in CLI.
- Maintainer vector DB lifecycle and requirement-named APIs (`REQ-API-001..006`) are implemented.
- Remaining high-impact gaps are Webex delivery parity, draft-tracker user route, and richer meeting-summary output.

## How Agents Should Work In This Repo
- Keep behavior deterministic and parser fallbacks explicit for external HTML/API changes.
- Preserve CLI/MCP semantic parity unless an intentional divergence is documented.
- Treat requirement IDs as contracts; include requirement mapping in feature/bug PR summaries.
- Do not weaken existing UX contracts (iterative flow, back/quit navigation) without explicit requirement change.

## Mandatory Change Gates (Feature And Bug-Fix)
Any feature addition or bug fix MUST include all of the following:
1. Code + tests
   - At least one CLI-path test and one parser/unit test for behavioral changes.
2. Documentation sync
   - Update impacted docs under `docs/`.
   - Update execution plan state (`active`, `completed`, tech debt delta).
3. Diagram sync
   - If control flow, architecture, or interaction flow changed, update PlantUML source and rendered SVG under `docs/design-docs/diagrams/`.
4. Knowledge capture
   - Update `Lessons.md` with new implementation lessons.
   - Update `coding_practices.md` if standards/review/test expectations changed.
5. Validation
   - Run `python -m pytest -q tests` (or `python3 -m pytest -q tests`) before finalizing.

## Source-of-Truth Files
- Requirements contract: `requirements.txt`
- Runtime architecture: `ARCHITECTURE.md`
- Onboarding/implementation baseline: `docs/product-specs/new-user-onboarding.md`
- Design docs index: `docs/design-docs/index.md`
- Internal API contract: `docs/design-docs/internal-api-contract.md`
- Active and completed plans: `docs/exec-plans/active/`, `docs/exec-plans/completed/`
- Tech debt register: `docs/exec-plans/tech-debt-tracker.md`
- Quality/reliability/security standards:
  - `docs/QUALITY_SCORE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Cross-feature memory and standards:
  - `Lessons.md`
  - `coding_practices.md`
