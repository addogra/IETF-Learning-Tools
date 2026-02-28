Author: Aditya Dogra
Date: 2026-02-28
Status: Active
Plan: Requirements Parity Phase 1

# Objective
Close the highest-impact gaps between `requirements.txt` and the current implementation while preserving existing CLI and MCP behaviors.

# Why This Plan Exists
The codebase already implements core WG resolution, charter/draft/discussion retrieval, meeting views, MCP tool exposure, and daily email delivery. However, several normative requirements remain unimplemented or partially implemented.

Primary uncovered requirement clusters:
- `REQ-FEAT-001`, `REQ-VDB-001..003`, `REQ-MAINT-001..006`: technology-to-WG onboarding and charter vector DB lifecycle.
- `REQ-MODE-001`: Webex bot delivery mode parity.
- `REQ-FEAT-010`, `REQ-API-005`: draft tracker.
- `REQ-FEAT-003`: full charter output (current default flow summarizes).
- `REQ-FEAT-006`: meeting update output lacks agenda/minutes summaries.
- `REQ-INPUT-002`, `REQ-UX-001`: iterative next-options loop + explicit quit path after actions.
- `REQ-MAINT-007`: maintainer garbage collector for docs/architecture drift.

# Scope
In scope:
- Build minimum viable charter knowledge base lifecycle:
  - WG crawl/list
  - charter extraction pipeline
  - local vector index creation/rebuild with safe delete semantics
  - deterministic query matching with AND semantics for compound intents
- Implement normative API wrappers listed in Section 9 of `requirements.txt`.
- Add CLI + MCP support for:
  - technology onboarding prompt/route
  - full charter view mode
  - draft tracker
  - richer last-2-meetings summaries (agenda + minutes summary text)
- Add iterative CLI interaction loop with explicit `Quit`.
- Introduce initial Webex integration surface (command map + adapter scaffold) to unblock parity work.
- Add maintainer garbage-collector command that reports requirement/documentation/architecture mismatches.

Out of scope for this phase:
- Vendor-implementation signal enrichment for draft tracker (keep behind a flag and mark optional).
- Full production deployment topology for Webex (focus on command parity + tests first).

# Workstreams
1. Knowledge Base + Matching Foundation
- Implement charter corpus builder and local index metadata.
- Add `rebuild_wg_charter_db(force_delete_old: bool = True)` and `get_db_metadata()`.
- Add `suggest_wgs_by_technology(..., require_all_terms=True)` with deterministic scoring/rationale.

2. API Contract Alignment
- Add requirement-named API functions in `ietf.py` (or dedicated facade) without breaking current call sites.
- Keep existing functions as compatibility wrappers during migration.

3. User Feature Gaps
- Add full charter output path (`get_wg_charter`) with non-truncated response mode.
- Extend meeting update pipeline to generate short agenda/minutes summaries.
- Implement `track_draft_or_rfc(identifier, include_vendor_signals=False)`.

4. UX + Delivery Mode Parity
- Add iterative options/quit loop to CLI post-action flow.
- Add Webex adapter skeleton and command parity checks for implemented features.

5. Maintainer Operations
- Add "Garbage Collector" command that validates:
  - requirement IDs mapped to features/tests/docs
  - architecture/source drift checks
  - stale or missing execution-plan entries

# Test Plan
For each new feature area, add at least:
- one CLI-path test (`tests/test_cli.py` expansion),
- one parser/unit test (`tests/test_ietf_*.py` or module-specific test),
- MCP registration/runtime test updates (`tests/test_server_mcp.py`),
- delivery-mode parity tests for Webex adapter contracts.

Mandatory gate:
- `python -m pytest -q tests`

# Exit Criteria
- `REQ-FEAT-001`, `REQ-FEAT-003`, `REQ-FEAT-006`, `REQ-FEAT-010` implemented with tests.
- `REQ-API-001..006` function contracts available and documented.
- `REQ-MODE-001` no longer blocked by missing Webex surface.
- `REQ-INPUT-002` / `REQ-UX-001` satisfied in CLI interaction flow.
- Remaining lower-priority issues tracked in `tech-debt-tracker.md`.
