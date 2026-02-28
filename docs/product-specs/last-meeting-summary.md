
# Last Meeting Summary Spec

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

## Delivery Surfaces
- CLI option `7`
- MCP tool `summary_of_last_ietf_meeting()`
- Included in daily report/email content filtered by subscribed WGs
