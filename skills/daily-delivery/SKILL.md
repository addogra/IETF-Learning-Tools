
# Skill: daily-delivery

## Purpose
Generate per-user daily WG reports and deliver via SMTP with retry/backoff.

## Inputs
- Subscription DB
- WG charter data
- SMTP configuration

## Steps
1. Load subscriptions and group by user.
2. Build per-user report content.
   - Include charter summary.
   - Include updates from last 2 IETF meetings (agenda + minutes).
   - Include upcoming IETF agenda summaries (if available for subscribed WGs).
   - Include last IETF meeting minutes summaries (if available for subscribed WGs).
3. Send emails with retry/backoff/jitter.
4. Record delivered/skipped/failed outcomes.
5. Persist report artifact to `reports/`.

## Outputs
- Delivery status summary and saved report file

## Failure Handling
- Missing SMTP config falls back to defaults.
- Non-email subscription IDs are skipped.
- Send failures are reported per recipient.
- Daily discussion-update emails are skipped when there are no last-day discussions.

## Test Coverage
- `tests/test_daily_delivery.py`
- `tests/test_server_mcp.py::send_daily_emails_now` (tool registration path)
