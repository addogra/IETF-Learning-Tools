
# Upcoming IETF Agenda Spec

## Requirement Mapping

- `REQ-FEAT-008`: discover upcoming IETF events + important dates and summarize WG agendas where published.

## Feature
Agenda of upcoming IETF meeting.

## Behavior
1. Read upcoming event metadata from `https://datatracker.ietf.org/meeting/important-dates/`.
2. Identify next planned IETF events (number, date, place).
3. Capture important details for each next planned event:
   - IETF Online Registration Opens
   - Final agenda to be published
   - Internet-Draft submission cut-off
   - Registration cancellation cut-off
   - Agenda link (`https://datatracker.ietf.org/meeting/<number>/agenda.txt`)
4. Fetch `https://datatracker.ietf.org/meeting/<number>/agenda.txt` for the next event.
5. Do not print full WG agenda body; output agenda links only.
7. If `agenda.txt` is minimal/boilerplate and today is earlier than the event's
   `Final agenda to be published` milestone, return:
   - `Agenda is NOT yet published, for this IETF-<Number>,Final agenda will be published on <Date>.`
8. Treat `Preliminary Agenda published` from important-dates as equivalent for
   the final-agenda milestone label in output.

## Output
Header:
- `Next IETF events planned and dates and location`
- `IETF <Number> - Dates <date> - Place <place>`
- `Important details (IETF <Number>)`

Body:
- `Agenda link - for IETF-<Number>: https://datatracker.ietf.org/meeting/<number>/agenda.txt`
- If agenda not yet published for the nearest event:
  - `Agenda is NOT yet published, for this IETF-<Number>,Final agenda will be published on <Date>.`

## Current Status (Coded, Not Runtime-Verified Here)

- Important-dates parsing is coded.
- `agenda.txt` parsing for upcoming meeting is coded.
- WG agenda filtering and summary generation is coded.
- Minimal-agenda readiness check and pre-final-agenda notice is coded.

Status:
- `REQ-FEAT-008`: **Coded**.

## Delivery Surfaces
- CLI option `5`
- MCP tool `agenda_of_upcoming_ietf_meeting()`
- Included in daily report/email content filtered by subscribed WGs
