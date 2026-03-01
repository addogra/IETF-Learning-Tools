
# Meeting Updates Spec

## Requirement Mapping

- `REQ-FEAT-006`: return updates for last 2 WG meetings including agenda and minutes.
- Filter rule: only include meetings labeled `IETF <number>`.

## Input
WG acronym/name resolved to canonical WG.

## Data Source
`https://datatracker.ietf.org/wg/<acronym>/meetings/`

## Output
For each of last 2 meetings:
- meeting label
- agenda links
- minutes links

## Current Status (Coded, Not Runtime-Verified Here)

- Link extraction for agenda/minutes from last 2 meetings is coded.
- Meeting filtering enforces `IETF <number>` matching.
- Results are sorted by IETF meeting number (newest first) and limited to 2.

Status:
- `REQ-FEAT-006`: **Coded**.

## Delivery Surfaces
- CLI option `4`
- MCP tool `updates_from_last_2_ietf_meetings(query)`
- Included in daily report/email content per subscribed WG

## Related Tech Debt

- `TD-009`: add fixture-backed meeting-page parser coverage.
