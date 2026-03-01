Date: 2026-03-01
Status: Completed
Plan: REQ-FEAT-006 - Updates From Last 2 IETF Meetings

# Objective
Implement `REQ-FEAT-006` in user-facing onboarding flow and supporting parsers.

# Requirement Mapping
- `REQ-FEAT-006`: "Updates from last 2 IETF meetings"
- Source: `https://datatracker.ietf.org/wg/<wg>/meetings/`
- Constraint: include only meetings matching `IETF <number>`.
- Output: return agenda and minutes for the last 2 WG meetings.

# Scope Delivered
1. CLI onboarding WG menu now includes:
   - `4. Updates from last 2 IETF meetings`
2. Meeting extractor now enforces IETF-only meeting selection:
   - parses meeting number from URL/text,
   - ignores non-IETF/interim entries,
   - sorts by meeting number descending,
   - returns latest 2.
3. Output formatting explicitly separates:
   - `Agenda:` links
   - `Minutes:` links
4. Per-feature PlantUML diagrams are present for `REQ-FEAT-001..006`.

# Files Updated (Primary)
- `src/ietf_wg_agent/cli.py`
- `src/ietf_wg_agent/ietf.py`
- `src/ietf_wg_agent/server.py`
- `tests/test_cli.py`
- `tests/test_ietf_meetings.py`
- `tests/test_server_mcp.py`
- `docs/product-specs/meeting-updates.md`
- `docs/product-specs/new-user-onboarding.md`
- `docs/design-docs/internal-api-contract.md`
- `docs/design-docs/modules/cli-module.md`
- `docs/design-docs/modules/ietf-module.md`
- `docs/design-docs/modules/server-module.md`
- `docs/design-docs/diagrams/req-feat-006-flow.puml`
- `docs/design-docs/diagrams/req-feat-006-flow.svg`

# Validation
- Focused run:
  - `PYTHONPATH=src python3 -m pytest -q tests/test_ietf_meetings.py tests/test_cli.py tests/test_server_mcp.py`
- Full regression gate:
  - `PYTHONPATH=src python3 -m pytest -q tests`

# Outcome
`REQ-FEAT-006` is implemented in CLI and MCP-facing formatting paths with parser constraints aligned to requirement wording (`IETF <number>` only) and regression tests covering parser behavior and user-visible output.
