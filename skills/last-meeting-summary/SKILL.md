
# Skill: last-meeting-summary

## Purpose
Summarize WG meeting minutes for the last completed IETF meeting.

## Inputs
- IETF meetings index and meeting pages
- WG meetings pages
- Minutes pages per WG

## Steps
1. Detect last completed IETF meeting (by meeting end date).
2. Traverse WG meetings pages for that meeting number.
3. Collect agenda/minutes links.
4. Include only WGs with published minutes.
5. Summarize minutes text for each included WG.
6. Do not prompt for daily update registration in this flow.

## Outputs
- Header: `IETF <Number> - Dates - Place`
- Per-WG minutes summary lines

## Failure Handling
- If last meeting cannot be determined, return domain error.
- If WG has no meeting/minutes, skip it.
- If minutes page fetch fails, include fallback summary text.

## Test Coverage
- `tests/test_ietf_last_meeting.py`
- `tests/test_cli.py::test_cli_option_7_last_meeting_summary_flow`
