# Internal API Contract (Requirement-Named Surface)

Date: 2026-02-28
Scope: REQ-API-001..006 and maintainer parity traceability

## Purpose
This document defines the normative internal API names from `requirements.txt`, their status, where they are implemented, and how they are validated.

## Contract Matrix

| Requirement | API Name | Signature | Status | Current Implementation Location | Notes |
|---|---|---|---|---|---|
| REQ-API-001 | `rebuild_wg_charter_db` | `(force_delete_old: bool = True) -> RebuildResult` | Implemented | `src/ietf_wg_agent/ietf.py` | Rebuilds local DB, deletes old file by default, safe to rerun. |
| REQ-API-001 | `get_db_metadata` | `() -> DbMetadata` | Implemented | `src/ietf_wg_agent/ietf.py` | Reads DB metadata without full payload load in callers. |
| REQ-API-002 | `resolve_wg_name` | `(user_input: str) -> WgResolutionResult` | Implemented | `src/ietf_wg_agent/ietf.py` | Wrapper over WG catalog + suggestion logic. |
| REQ-API-002 | `suggest_wgs_by_technology` | `(query: str, top_k: int = 10, require_all_terms: bool = True) -> list[WgMatch]` | Implemented | `src/ietf_wg_agent/ietf.py` | Vector-DB matching over charter + documents corpus. |
| REQ-API-003 | `get_wg_charter` | `(wg_id: str) -> CharterResult` | Pending | Not yet defined | Existing equivalent behavior: `fetch_charter_text`. Missing contract wrapper/result type. |
| REQ-API-003 | `get_wg_active_drafts` | `(wg_id: str, limit: int = 5) -> list[DraftResult]` | Pending | Not yet defined | Existing equivalent behavior: `fetch_top_active_drafts`. |
| REQ-API-003 | `get_wg_discussion_summary` | `(wg_id: str, window_days: int = 90) -> DiscussionSummary` | Pending | Not yet defined | Existing underlying fetch/summarize pieces exist; contract wrapper missing. |
| REQ-API-003 | `get_wg_last_two_meeting_updates` | `(wg_id: str) -> MeetingUpdates` | Pending | Not yet defined | Existing equivalent behavior: `fetch_updates_from_last_two_meetings`. |
| REQ-API-004 | `get_upcoming_ietf_agenda_summary` | `() -> UpcomingMeetingSummary` | Pending | Not yet defined | Existing equivalent behavior: `fetch_upcoming_ietf_agenda`. |
| REQ-API-004 | `get_last_ietf_meeting_summary` | `() -> LastMeetingSummary` | Pending | Not yet defined | Existing equivalent behavior: `fetch_summary_of_last_ietf_meeting`. |
| REQ-API-005 | `track_draft_or_rfc` | `(identifier: str, include_vendor_signals: bool = False) -> DraftTrackerResult` | Pending | Not yet defined | Feature and wrapper not implemented. |
| REQ-API-006 | `run_daily_wg_update` | `(wg_id: str, notify: bool = True) -> DailyUpdateResult` | Pending | Not yet defined | Existing daily pipeline is user/subscription oriented, not WG-contract wrapper. |
| REQ-API-006 | `schedule_daily_updates` | `(subscription: SubscriptionConfig) -> SchedulerResult` | Pending | Not yet defined | Existing schedulers exist; contract wrapper/result type missing. |

## Implemented API Details

### `rebuild_wg_charter_db(force_delete_old: bool = True) -> RebuildResult`
Behavior:
- Crawls active WGs from `https://datatracker.ietf.org/wg/`.
- Fetches `about` and `documents` pages for each WG.
- Extracts full charter text and documents-page text.
- Builds deterministic sparse TF-IDF vectors.
- Writes DB payload to `data/wg_charter_vector_db.json`.
- Deletes old DB first when `force_delete_old=True`.

Failure model:
- Raises `DatatrackerError` when no WG corpus can be built or source fetch fails catastrophically.
- Partial WG failures are tracked in payload `errors` and do not abort full rebuild.

### `get_db_metadata() -> DbMetadata`
Behavior:
- Returns existence, schema version, build timestamp, counts, and checksum.
- If DB does not exist, returns `exists=False` with zeroed stats.

### `resolve_wg_name(user_input: str) -> WgResolutionResult`
Behavior:
- Fetches WG catalog from Datatracker API.
- Resolves exact/prefix/contains WG match.
- Returns ranked suggestions when no direct match exists.

### `suggest_wgs_by_technology(query: str, top_k: int = 10, require_all_terms: bool = True) -> list[WgMatch]`
Behavior:
- Loads persisted vector DB.
- Tokenizes query and builds query vector using DB IDF.
- Scores each WG by cosine similarity.
- Optional strict AND semantics via `require_all_terms=True`.
- Returns ranked `WgMatch` list with matched-term justification.

## Maintainer Enforcement
`ietf-wg-maintainer garbage-collector` checks the presence of all contract API names in `src/ietf_wg_agent/ietf.py` and reports missing functions. This provides explicit drift visibility until full API parity is delivered.

## Validation Coverage
- `tests/test_ietf_vector_db.py`
  - rebuild lifecycle and metadata correctness
  - idempotent replace semantics
  - technology matching behavior
  - documents-section term ingestion coverage
- `tests/test_maintainer.py`
  - maintainer command formatting
  - garbage collector API-missing detection
  - garbage collector pass behavior under satisfied constraints

## Forward Plan
Remaining wrappers and result models are tracked in:
- `docs/exec-plans/active/2026-02-28-requirements-parity-phase-1.md`
- `docs/exec-plans/tech-debt-tracker.md` (`TD-003`, `TD-007`)
