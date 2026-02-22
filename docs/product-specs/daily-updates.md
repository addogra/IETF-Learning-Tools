Author: Aditya Dogra

# Daily Updates Spec

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

## Delivery Surfaces
- CLI option `5`
- MCP tools:
  - `daily_updates_summary(query)`
  - `run_daily_updates_summary_now()`
  - `send_daily_updates_now()`
- Daily delivery pipeline and scheduler command
