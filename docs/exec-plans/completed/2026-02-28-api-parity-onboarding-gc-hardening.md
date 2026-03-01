Date: 2026-02-28
Status: Completed
Plan: API Parity + Onboarding + Garbage Collector Hardening

# Objective
Deliver the next priority follow-ups after vector DB baseline:
1. Implement `REQ-API-003..006` wrappers.
2. Wire user-facing technology onboarding in CLI/MCP.
3. Add deeper garbage-collector semantic checks.

# Completed
1. Implemented requirement-named API wrappers in `src/ietf_wg_agent/ietf.py`:
   - `get_wg_charter`
   - `get_wg_active_drafts`
   - `get_wg_discussion_summary`
   - `get_wg_last_two_meeting_updates`
   - `get_upcoming_ietf_agenda_summary`
   - `get_last_ietf_meeting_summary`
   - `track_draft_or_rfc`
   - `run_daily_wg_update`
   - `schedule_daily_updates`
2. Added contract result models in `ietf.py`:
   - `CharterResult`, `DraftResult`, `DiscussionSummary`, `MeetingUpdates`
   - `UpcomingMeetingSummary`, `LastMeetingSummary`
   - `DraftTrackerResult`, `SubscriptionConfig`, `SchedulerResult`, `DailyUpdateResult`
3. Wired user-facing technology onboarding:
   - CLI User Type A prompt (`What technology area are you interested in?`) and ranked WG selection from vector DB.
   - MCP tool `technology_onboarding(query, top_k=10, require_all_terms=True)`.
4. Deepened maintainer garbage collector semantic rules:
   - API-doc status alignment checks.
   - Entrypoint alignment (`ARCHITECTURE.md` vs `pyproject.toml`/`setup.py`).
   - Module-doc index alignment checks.
   - Vector DB schema-doc token checks.

# Tests Added/Updated
- `tests/test_ietf_contract_api.py` (new)
- `tests/test_cli.py` (technology onboarding flow)
- `tests/test_server_mcp.py` (new tool registration assertion)
- `tests/test_maintainer.py` (semantic checks coverage)

# Verification
Command:
```bash
PYTHONPATH=src python3 -m pytest -q tests
```
Result:
- `55 passed, 1 warning`

Command:
```bash
PYTHONPATH=src python3 -m ietf_wg_agent.maintainer garbage-collector
```
Result:
- Semantic/API consistency checks pass after documentation synchronization.

# Remaining
- Expose draft tracker on CLI/MCP user path.
- Webex delivery mode parity.
- Richer meeting-summary output.
