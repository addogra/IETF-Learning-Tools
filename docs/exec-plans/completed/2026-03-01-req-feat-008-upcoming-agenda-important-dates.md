Date: 2026-03-01
Status: Completed
Plan: REQ-FEAT-008 - Upcoming IETF Agenda via Important Dates + agenda.txt

# Objective
Implement REQ-FEAT-008 in the iterative onboarding menu and align data-source behavior to the requirement contract.

# Requirement Mapping
- Source 1: `https://datatracker.ietf.org/meeting/important-dates/`
- Source 2: `https://datatracker.ietf.org/meeting/<IETF-NUMBER>/agenda.txt`
- Output requirements:
  - next planned IETF events with dates/location
  - required important dates for next meeting:
    - IETF Online Registration Opens
    - Final agenda to be published
    - Internet-Draft submission cut-off
    - Registration cancellation cut-off
  - `IETF <number> - <dates> - <place>`
  - `Working Group <name> - summarized agenda`

# Scope Delivered
1. Added CLI WG-menu option `5. Agenda of upcoming IETF meeting`.
2. Reworked upcoming-agenda parser path to:
   - parse events + milestone dates from `important-dates` page,
   - fetch next-meeting `agenda.txt`,
   - index agenda lines by WG acronym,
   - include only WGs with published agenda entries.
3. Updated MCP/daily formatting for REQ-FEAT-008 output style.
4. Added/updated tests for parser path, CLI option, and MCP tool output.
5. Added PlantUML flows for REQ-FEAT-007 and REQ-FEAT-008 and updated architecture diagram.

# Files Updated (Primary)
- `src/ietf_wg_agent/ietf.py`
- `src/ietf_wg_agent/cli.py`
- `src/ietf_wg_agent/server.py`
- `src/ietf_wg_agent/daily.py`
- `tests/test_ietf_upcoming_agenda.py`
- `tests/test_cli.py`
- `tests/test_server_mcp.py`
- `requirements.txt`
- `docs/product-specs/upcoming-agenda.md`
- `docs/product-specs/new-user-onboarding.md`
- `docs/design-docs/modules/cli-module.md`
- `docs/design-docs/modules/ietf-module.md`
- `docs/design-docs/modules/server-module.md`
- `docs/design-docs/internal-api-contract.md`
- `docs/design-docs/diagrams/req-feat-007-flow.puml`
- `docs/design-docs/diagrams/req-feat-008-flow.puml`

# Validation
- Targeted: `PYTHONPATH=src python3 -m pytest -q tests/test_ietf_upcoming_agenda.py tests/test_cli.py tests/test_server_mcp.py tests/test_daily_delivery.py tests/test_ietf_contract_api.py`
- Full: `PYTHONPATH=src python3 -m pytest -q tests`

# Outcome
REQ-FEAT-008 is integrated into onboarding flow and now uses requirement-specified sources (`important-dates` and `agenda.txt`) while preserving deterministic output and skip behavior for WGs with no published upcoming agenda.
