
# Skill: upcoming-agenda

## Purpose
Find the next IETF meeting and summarize available WG agendas.

## Inputs
- IETF meetings index and meeting detail page
- WG meetings pages for all working groups

## Steps
1. Determine next IETF meeting number.
2. Read meeting dates/place from meeting detail page.
3. Traverse WG meetings pages and collect agenda links for the target meeting.
4. Fetch agenda pages and summarize agenda content.
5. Skip WGs with no published agenda.
6. Do not prompt for daily update registration in this flow.

## Outputs
- Header: `IETF <Number> - Dates - Place`
- Per WG agenda summary lines:
  - `Working Group <Name> ...`

## Failure Handling
- If next meeting cannot be determined, return domain error.
- If agenda missing for WG, skip WG.
- If agenda page fetch fails, include fallback summary text.

## Test Coverage
- `tests/test_ietf_upcoming_agenda.py`
- `tests/test_cli.py::test_cli_option_6_upcoming_agenda_flow`
