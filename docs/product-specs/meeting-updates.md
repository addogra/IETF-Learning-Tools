
# Meeting Updates Spec

## Requirement Mapping

- `REQ-FEAT-006`: return updates for last 2 WG meetings including agenda summary + minutes summary.

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
- Meeting label inference is coded.
- Requirement-level agenda/minutes summary text in this feature path is not fully aligned.

Status:
- `REQ-FEAT-006`: **Partially coded**.

## Delivery Surfaces
- CLI option `4`
- MCP tool `updates_from_last_2_ietf_meetings(query)`
- Included in daily report/email content per subscribed WG

## Related Tech Debt

- `TD-005`: meeting update output lacks agenda/minutes summaries.
