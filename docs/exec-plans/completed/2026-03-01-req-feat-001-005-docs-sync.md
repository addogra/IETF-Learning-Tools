Date: 2026-03-01
Status: Completed
Plan: REQ-FEAT-001..005 Documentation + Architecture Sync

# Objective
Synchronize architecture/design/onboarding/plan documents with the implemented REQ-FEAT-001..005 behavior and add a PlantUML architecture artifact for the full flow.

# Requirements Covered
- `REQ-FEAT-001`: New-user technology onboarding
- `REQ-FEAT-002`: WG name resolution
- `REQ-FEAT-003`: Summary of WG (complete charter, non-truncated)
- `REQ-FEAT-004`: Active drafts (bounded output for performance)
- `REQ-FEAT-005`: Draft discussions in a WG (last 3 months)

# What Was Updated
1. Architecture docs refreshed to match current runtime behavior:
   - `ARCHITECTURE.md`
   - `docs/DESIGN.md`
2. Design module docs refreshed:
   - `docs/design-docs/index.md`
   - `docs/design-docs/onboarding-flow.md`
   - `docs/design-docs/internal-api-contract.md`
   - `docs/design-docs/modules/cli-module.md`
   - `docs/design-docs/modules/ietf-module.md`
3. Product/onboarding specs refreshed:
   - `docs/product-specs/new-user-onboarding.md`
   - `docs/product-specs/wg-summary-and-drafts.md`
   - `docs/product-specs/discussion-summary.md`
4. Planning/debt docs refreshed:
   - `docs/PLANS.md`
   - `docs/exec-plans/tech-debt-tracker.md`
   - `docs/exec-plans/completed/README.md`
5. Added architecture artifact pair (PlantUML source + SVG render):
   - `docs/design-docs/diagrams/req-feat-001-005-architecture.puml`
   - `docs/design-docs/diagrams/req-feat-001-005-architecture.svg`

# Code/Test Alignment Changes Included
- MCP `summary_of_wg(query)` now returns complete charter text to align REQ-FEAT-003 with CLI behavior.
- Added CLI prompt-contract regression test (clean Type A prompt text).
- Added MCP summary regression test (full charter output).

# Key Design Notes
- Onboarding slice (`REQ-FEAT-001..005`) is treated as complete for CLI.
- `REQ-FEAT-004` output remains intentionally capped at 10 drafts in onboarding flow to balance latency and usefulness.
- Discussion date parsing remains metadata-first to avoid false positives from subject deadlines.

# Validation Commands
```bash
PYTHONPATH=src python3 -m pytest -q tests/test_cli.py
PYTHONPATH=src python3 -m pytest -q tests/test_server_mcp.py
PYTHONPATH=src python3 -m pytest -q tests
```

# Exit Outcome
- Documentation and architecture artifacts now reflect current implemented behavior for REQ-FEAT-001..005.
- Remaining non-REQ-FEAT-001..005 gaps are tracked in tech debt (`TD-002`, `TD-003`, `TD-005`, `TD-009`, `TD-010`, `TD-011`).
