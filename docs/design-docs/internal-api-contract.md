# Internal API Contract (Requirement-Named Surface)

Date: 2026-02-28
Scope: REQ-API-001..006 implementation surface and maintainer drift checks

## Purpose
This document defines the normative internal API names from `requirements.txt`, their implementation status, and how they map to the current code.

## Contract Matrix

| Requirement | API Name | Signature | Status | Current Implementation Location | Notes |
|---|---|---|---|---|---|
| REQ-API-001 | `rebuild_wg_charter_db` | `(force_delete_old: bool = True) -> RebuildResult` | Implemented | `src/ietf_wg_agent/ietf.py` | Rebuilds local DB, deletes old file by default, safe to rerun. |
| REQ-API-001 | `get_db_metadata` | `() -> DbMetadata` | Implemented | `src/ietf_wg_agent/ietf.py` | Reads DB metadata. |
| REQ-API-002 | `resolve_wg_name` | `(user_input: str) -> WgResolutionResult` | Implemented | `src/ietf_wg_agent/ietf.py` | Wrapper over WG catalog + suggestion logic. |
| REQ-API-002 | `suggest_wgs_by_technology` | `(query: str, top_k: int = 10, require_all_terms: bool = True) -> list[WgMatch]` | Implemented | `src/ietf_wg_agent/ietf.py` | Vector-DB matching over charter + documents corpus. |
| REQ-API-003 | `get_wg_charter` | `(wg_id: str) -> CharterResult` | Implemented | `src/ietf_wg_agent/ietf.py` | Resolves WG and returns complete charter text. |
| REQ-API-003 | `get_wg_active_drafts` | `(wg_id: str, limit: int = 5) -> list[DraftResult]` | Implemented | `src/ietf_wg_agent/ietf.py` | Wrapper over active-draft parser with normalized result type. |
| REQ-API-003 | `get_wg_discussion_summary` | `(wg_id: str, window_days: int = 90) -> DiscussionSummary` | Implemented | `src/ietf_wg_agent/ietf.py` | Windowed discussion summary wrapper with post list and summary text. |
| REQ-API-003 | `get_wg_last_two_meeting_updates` | `(wg_id: str) -> MeetingUpdates` | Implemented | `src/ietf_wg_agent/ietf.py` | Wrapper for last-two-meeting agenda/minutes updates. |
| REQ-API-004 | `get_upcoming_ietf_agenda_summary` | `() -> UpcomingMeetingSummary` | Implemented | `src/ietf_wg_agent/ietf.py` | Wraps upcoming-meeting agenda extraction. |
| REQ-API-004 | `get_last_ietf_meeting_summary` | `() -> LastMeetingSummary` | Implemented | `src/ietf_wg_agent/ietf.py` | Wraps last-completed-meeting summary extraction. |
| REQ-API-005 | `track_draft_or_rfc` | `(identifier: str, include_vendor_signals: bool = False) -> DraftTrackerResult` | Implemented | `src/ietf_wg_agent/ietf.py` | Datatracker document metadata tracker wrapper. |
| REQ-API-006 | `run_daily_wg_update` | `(wg_id: str, notify: bool = True) -> DailyUpdateResult` | Implemented | `src/ietf_wg_agent/ietf.py` | One-shot WG daily discussion summary with optional notification send. |
| REQ-API-006 | `schedule_daily_updates` | `(subscription: SubscriptionConfig) -> SchedulerResult` | Implemented | `src/ietf_wg_agent/ietf.py` | Registers subscription and optionally starts scheduler process. |

## Result Models Added
All contract wrappers return explicit result models declared in `ietf.py`:
- `CharterResult`, `DraftResult`, `DiscussionSummary`, `MeetingUpdates`
- `UpcomingMeetingSummary`, `LastMeetingSummary`
- `DraftTrackerResult`
- `SubscriptionConfig`, `SchedulerResult`, `DailyUpdateResult`

## Integration Surfaces
- CLI technology onboarding route: `src/ietf_wg_agent/cli.py`
  - input trigger: type `tech`
  - powered by `suggest_wgs_by_technology`
- MCP technology onboarding tool: `src/ietf_wg_agent/server.py`
  - tool: `technology_onboarding(query, top_k=10, require_all_terms=True)`

## Maintainer Enforcement
`ietf-wg-maintainer garbage-collector` verifies:
1. API function-name presence in `ietf.py`.
2. API contract doc row presence and status alignment with code.
3. Entrypoint alignment across architecture docs and packaging files.
4. Module-doc index coverage.
5. Vector-DB schema doc token coverage for critical fields.

## Validation Coverage
- `tests/test_ietf_vector_db.py`
- `tests/test_ietf_contract_api.py`
- `tests/test_cli.py`
- `tests/test_server_mcp.py`
- `tests/test_maintainer.py`
