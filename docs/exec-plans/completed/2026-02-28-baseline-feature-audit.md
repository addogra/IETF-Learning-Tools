Author: Aditya Dogra
Date: 2026-02-28
Status: Completed
Plan: Baseline Feature Audit Against Requirements

# Objective
Establish an explicit baseline of what is already implemented and test-covered before starting requirements-parity work.

# Outcome
Completed a full code and test audit across:
- `src/ietf_wg_agent/*.py`
- `scripts/bootstrap.py`
- `tests/*.py`
- `requirements.txt`
- architecture/product docs relevant to execution planning

# Implemented And Verified
1. WG Resolution + Suggestions
- Fetch WG catalog from Datatracker API.
- Resolve acronym/full-name inputs.
- Suggest nearest WGs for ambiguous/typo inputs.
- Evidence:
  - `src/ietf_wg_agent/ietf.py`
  - `tests/test_ietf_suggestions.py`
  - `tests/test_cli.py` (suggestion flow)

2. WG Charter, Active Drafts, Discussion Summary
- Charter extraction from WG about page.
- Top 5 active drafts with status and abstract extraction.
- Last-3-month discussion summary and last-day discussion summary.
- Evidence:
  - `src/ietf_wg_agent/ietf.py`
  - `src/ietf_wg_agent/summarizer.py`
  - `tests/test_ietf_drafts.py`
  - `tests/test_ietf_discussions.py`

3. Meeting Views
- Last 2 WG meeting updates (agenda/minutes links).
- Upcoming IETF meeting header + WG agenda summaries.
- Last completed IETF meeting header + WG minutes summaries.
- Evidence:
  - `src/ietf_wg_agent/ietf.py`
  - `tests/test_ietf_meetings.py`
  - `tests/test_ietf_upcoming_agenda.py`
  - `tests/test_ietf_last_meeting.py`

4. Delivery Surfaces (Current)
- CLI feature menu (options 1-7).
- MCP tool registration and execution entrypoint.
- Daily report and email delivery with retry/backoff/jitter.
- Discussion-update scheduler (once/loop mode).
- Evidence:
  - `src/ietf_wg_agent/cli.py`
  - `src/ietf_wg_agent/server.py`
  - `src/ietf_wg_agent/daily.py`
  - `src/ietf_wg_agent/notifier.py`
  - `src/ietf_wg_agent/discussion_scheduler.py`
  - `tests/test_server_mcp.py`
  - `tests/test_daily_delivery.py`
  - `tests/test_discussion_scheduler.py`

5. Tooling + Packaging Baseline
- Cross-platform bootstrap path with Python version handling for MCP.
- Console entrypoint wiring for CLI/MCP/daily/scheduler.
- Evidence:
  - `scripts/bootstrap.py`
  - `tests/test_bootstrap.py`
  - `pyproject.toml`, `setup.py`

# Requirement Coverage Snapshot
Fully/mostly covered:
- WG resolution, draft extraction, discussion summaries, upcoming agenda, last meeting summary, daily-update suppression when no new posts, MCP tool exposure for implemented features.

Partially covered:
- `REQ-FEAT-003` (charter currently summarized by default in UI flows, not full output mode).
- `REQ-FEAT-006` (meeting updates return links, not agenda/minutes summaries).
- UX contract requiring iterative follow-up options with explicit quit path after each action.

Not covered:
- Technology onboarding via charter vector DB and maintainer rebuild lifecycle.
- Draft tracker feature.
- Webex delivery mode parity.
- Maintainer garbage collector.
- Normative internal API naming contract from Section 9.

# Follow-up
Uncovered and partial items were moved to:
- Active plan: `docs/exec-plans/active/2026-02-28-requirements-parity-phase-1.md`
- Tech debt tracker: `docs/exec-plans/tech-debt-tracker.md`
