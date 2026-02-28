
# Daily Updates Spec

## Requirement Mapping

- `REQ-FEAT-007`: summarize last-day activity and deliver updates only when activity exists.
- `REQ-REL-002`: notifications should be retry-safe.
- `REQ-REL-003`: skip outbound update when no new content exists.

## Feature
Daily updates from WG mailarchive.

## Input
WG acronym/name resolved to canonical WG and existing user subscriptions.

## Data Source
`https://mailarchive.ietf.org/arch/browse/<acronym>/`

## Behavior
- Summarize discussions from last 1 day.
- Start scheduler mode for recurring daily checks.
- Send email only when at least one discussion exists in last day.
- If no updates exist, do not send any email.

## Current Status (Coded, Not Runtime-Verified Here)

- Last-day discussion extraction is coded.
- Conditional email suppression when no updates exist is coded.
- SMTP retry/backoff/jitter behavior is coded.

Status:
- `REQ-FEAT-007`: **Coded**.
- `REQ-REL-002`: **Coded**.
- `REQ-REL-003`: **Coded**.

## Delivery Surfaces
- CLI option `5`
- MCP tools:
  - `daily_updates_summary(query)`
  - `run_daily_updates_summary_now()`
  - `send_daily_updates_now()`
- Daily delivery pipeline and scheduler command
