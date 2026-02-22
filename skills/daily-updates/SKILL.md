Author: Aditya Dogra

# Skill: daily-updates

## Purpose
Provide daily discussion updates for each subscribed WG, with conditional delivery.

## Inputs
- Subscription DB
- Mailarchive browse pages per WG
- Daily window (last 1 day)

## Steps
1. Fetch last-day discussions per subscribed WG.
2. Build per-user discussion summary only if at least one WG has updates.
3. Send email only for users with updates.
4. Expose scheduler mode for automatic daily execution.

## Outputs
- Last-day summary text
- Optional email delivery status
- Scheduler command/mode for recurring execution

## Failure Handling
- If no updates found, do not send email.
- If email config/send fails, report skipped/failed recipients.

## Test Coverage
- `tests/test_ietf_discussions.py`
- `tests/test_daily_delivery.py`
- `tests/test_cli.py::test_cli_option_5_daily_updates_flow`
