
# Daily Module (`src/ietf_wg_agent/daily.py`)

## Purpose
Generate per-user daily summaries and trigger email delivery.

## Control Flow
1. Load subscriptions and group by user.
2. Build one report per user using WG charter summary.
3. Build daily discussion-update reports (last 1 day) for users with updates.
4. Send each report via SMTP notifier.
5. Collect delivery stats (delivered/skipped/errors).
6. Persist final combined report to `reports/`.

Also includes upcoming IETF agenda summaries for each user's subscribed WGs.
Also includes last IETF meeting minutes summaries for each user's subscribed WGs.

## Daily Updates Rule
- Discussion-update emails are sent only when at least one last-day discussion exists.
- If no update exists, no daily-update email is sent.
