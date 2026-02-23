Author: Aditya Dogra

# ietf-wg-agent

A local MCP server + CLI agent for IETF Working Group discovery and charter summaries.

## What it does

- Accepts a WG input in short form or full name (example: `LSR` or `Link State Routing`).
- Resolves the WG via IETF Datatracker.
- Provides the option `Summary of WG` by fetching the charter from Datatracker and summarizing it.
- Allows registering WG subscriptions for daily summaries.
- Includes a daily runner that generates a report from subscriptions and sends email.

## Install (Cross-Platform)

Python compatibility policy:
- Base app (CLI + daily features): Python `3.9+`
- MCP server (`ietf-wg-mcp`): Python `3.10+`
- Tested in CI on Python `3.9`, `3.10`, `3.11`, and `3.12`

### Fast path (recommended)

From the project root:

macOS / Linux:

```bash
./scripts/setup.sh
```

Windows PowerShell:

```powershell
.\scripts\setup.ps1
```

Windows CMD:

```bat
scripts\setup.bat
```

### Make-based setup (macOS/Linux)

```bash
make setup
```

Useful setup variants:
- `make setup` -> install `.[full]`
- `make setup-base` -> install base dependencies only
- `make setup-mcp` -> install base + MCP dependencies with automatic Python 3.10+ upgrade path

Note: MCP dependency is installed only on Python 3.10+.  
On Python 3.9, setup still succeeds and MCP-specific runtime remains unavailable.
On Python 3.9, setup also pins `urllib3<2` automatically to avoid LibreSSL warnings.

### Seamless MCP setup (recommended for MCP users)

If you want MCP support, run:

```bash
./scripts/setup.sh --extras mcp
```

Behavior:
- If your current Python is 3.10+, MCP is installed into `.venv` (or your chosen `--venv`).
- If your current Python is 3.9 and a 3.10+ interpreter exists on PATH, setup auto-creates `.venv-mcp` and installs MCP there.
- If no 3.10+ interpreter is found, setup prints OS-specific install instructions and exits cleanly.

You can also force a specific interpreter:

```bash
./scripts/setup.sh --extras mcp --python python3.11
```

### Manual install (all platforms)

```bash
python -m venv .venv
```

Activate venv:
- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows CMD: `.venv\Scripts\activate.bat`

Then install:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -e ".[full]"
```

If editable mode fails in older toolchains:

```bash
pip install ".[full]"
```

### OS prerequisites

The bootstrap script prints guidance automatically, but if Python is missing:
- macOS: `brew install python@3.11`
- Debian/Ubuntu: `sudo apt update && sudo apt install -y python3 python3-venv python3-pip`
- RHEL/CentOS/Fedora/Rocky/AlmaLinux: `sudo dnf install -y python3 python3-pip`
- Windows: `winget install Python.Python.3.11`

## CLI app flow

```bash
ietf-wg-agent
```

Prompts:

- `Email for daily updates`
- `Working Group Name`
- Register for daily updates (shown only for option 5)
- Option `1. Summary of WG`
- Option `2. Active drafts` (top 5 drafts from WG documents + abstract)
- Option `3. Draft discussions in a WG` (summary of last 3 months from mailarchive)
- Option `4. Updates from last 2 IETF meetings` (agenda + minutes links)
- Option `5. Daily updates` (summary of last 1 day + scheduler start)
- Option `6. Agenda of upcoming IETF meeting` (next meeting + WG agenda summaries)
- Option `7. Summary of last IETF meeting` (last completed meeting + WG minutes summaries)

## Run daily job manually

```bash
ietf-wg-daily
```

This writes a report file to `reports/daily-YYYY-MM-DD.txt`.
It also attempts to send one email per subscribed user.

## Email configuration

Only user email is required in the app flow (it asks during `ietf-wg-agent`).
SMTP settings are optional and have defaults.

Default behavior:
- Host: `localhost`
- Port: `25`
- TLS/SSL: disabled
- Auth: disabled
- Sender: `ietf-wg-agent@localhost` (or SMTP username if provided)

Optional overrides:

```bash
export IETF_WG_SMTP_HOST="smtp.example.com"
export IETF_WG_SMTP_PORT="587"
export IETF_WG_SMTP_USERNAME="smtp-user"
export IETF_WG_SMTP_PASSWORD="smtp-password"
export IETF_WG_FROM_EMAIL="ietf-agent@example.com"
export IETF_WG_SMTP_STARTTLS="true"
export IETF_WG_SMTP_SSL="false"
export IETF_WG_SMTP_RETRIES="3"
export IETF_WG_SMTP_BACKOFF_SECONDS="1.5"
export IETF_WG_SMTP_JITTER_SECONDS="0.5"
```

Notes:
- Subscriber `user_id` values are treated as recipient email addresses.
- If a subscriber id is not an email format (no `@`), delivery is skipped.
- If SMTP env vars are missing, report generation still works and email step is skipped with a message.
- Emails are sent as multipart content (plain text + compact HTML sections per WG).
- Retry uses exponential backoff plus jitter:
  `base * 2^(attempt-1) + random(0, jitter_seconds)`.

## Schedule daily on macOS (launchd)

Create `~/Library/LaunchAgents/com.addogra.ietf-wg-daily.plist` with your environment and run:

```bash
launchctl load ~/Library/LaunchAgents/com.addogra.ietf-wg-daily.plist
```

(Use `ietf-wg-daily` command inside `ProgramArguments`.)

## MCP server

```bash
ietf-wg-mcp
```

Requirement: Python 3.10+ runtime with MCP extras installed.  
If you used the seamless setup on Python 3.9, activate `.venv-mcp` first.

Exposed MCP tools:

- `find_working_group(query)`
- `summary_of_wg(query)`
- `register_wg_daily_update(user_id, query)`
- `active_drafts_and_recent_rfcs(query)`
- `active_drafts(query)`
- `draft_discussions_summary(query)`
- `daily_updates_summary(query)`
- `updates_from_last_2_ietf_meetings(query)`
- `agenda_of_upcoming_ietf_meeting()`
- `summary_of_last_ietf_meeting()`
- `run_daily_summary_now()`
- `send_daily_emails_now()`
- `run_daily_updates_summary_now()`
- `send_daily_updates_now()`

## Notes

- Network access to `https://datatracker.ietf.org` and `https://mailarchive.ietf.org` is required.
- Subscription data is stored at `~/.ietf_wg_agent_subscriptions.json`.

## Testing

Run all tests locally:

```bash
source .venv/bin/activate
python -m pytest -q tests
```

CI is configured to run the full test suite on every push/pull request:
`.github/workflows/tests.yml`.

## Daily Updates Scheduler

Run one cycle:

```bash
ietf-wg-daily-updates --once
```

Run continuous scheduler loop (24h interval):

```bash
ietf-wg-daily-updates-scheduler
```
