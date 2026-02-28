
# Skill: meeting-updates

## Purpose
Fetch updates from the last 2 IETF WG meetings, including agenda and minutes links.

## Inputs
- WG acronym
- WG meetings page (`/wg/<acronym>/meetings/`)

## Steps
1. Fetch WG meetings page.
2. Identify links relevant to agenda/minutes.
3. Group links by meeting label (IETF number/date heuristic).
4. Return last 2 meetings with agenda/minutes URLs.
5. Do not prompt for daily update registration in this flow.

## Outputs
- Ordered list of meeting updates with:
  - meeting label
  - agendas list
  - minutes list

## Failure Handling
- Meetings page fetch failure returns domain-specific error.
- Missing agenda/minutes handled with explicit "Not found" output lines.

## Test Coverage
- `tests/test_ietf_meetings.py`
- `tests/test_cli.py::test_cli_option_4_meeting_updates_flow`
