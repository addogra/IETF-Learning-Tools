
# Upcoming IETF Agenda Spec

## Requirement Mapping

- `REQ-FEAT-008`: discover next IETF meeting metadata and summarize WG agendas where published.

## Feature
Agenda of upcoming IETF meeting.

## Behavior
1. Determine the next IETF meeting number.
2. Fetch meeting metadata (dates and place).
3. Traverse WG meetings pages and collect agenda links for that meeting.
4. Summarize each available agenda.
5. Skip WGs with no agenda published yet.

## Output
Header:
- `IETF <Number> - Dates - Place`

Body:
- `Working Group <WG Name> -- <agenda summary>`

## Current Status (Coded, Not Runtime-Verified Here)

- Next-meeting discovery is coded.
- WG agenda filtering and summary generation is coded.

Status:
- `REQ-FEAT-008`: **Coded**.

## Delivery Surfaces
- CLI option `6`
- MCP tool `agenda_of_upcoming_ietf_meeting()`
- Included in daily report/email content filtered by subscribed WGs
