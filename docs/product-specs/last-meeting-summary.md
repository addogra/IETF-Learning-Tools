
# Last Meeting Summary Spec

## Requirement Mapping

- `REQ-FEAT-009`: discover last completed IETF meeting metadata and summarize WG minutes.

## Feature
Summary of last IETF meeting.

## Behavior
1. Detect last completed IETF meeting.
2. Traverse each WG meetings page for that meeting.
3. Include only WGs with published minutes.
4. Summarize meeting minutes per WG.

## Output
Header:
- `IETF <Number> - Dates - Place`

Body:
- `Working Group <WG Name> -- meeting minutes summary`

## Current Status (Coded, Not Runtime-Verified Here)

- Last-completed-meeting detection is coded.
- WG minutes extraction and summary rendering is coded.

Status:
- `REQ-FEAT-009`: **Coded**.

## Delivery Surfaces
- CLI option `7`
- MCP tool `summary_of_last_ietf_meeting()`
- Included in daily report/email content filtered by subscribed WGs
