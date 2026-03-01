# CLI Module (`src/ietf_wg_agent/cli.py`)

## Purpose
Provide interactive user flow for REQ-FEAT-001..005 with explicit iterative navigation.

## User Types
- User Type A (new engineer): technology onboarding query.
- User Type B (experienced engineer): WG name input (short/full form).

## Iterative Control Flow
1. Render top-level user-type menu.
2. Resolve WG:
   - Type A: technology query -> vector DB matches -> user selects WG.
   - Type B: WG query -> resolution/suggestions -> user selects WG.
3. Enter WG feature menu.
4. Execute selected option:
   - 1: Summary of WG (complete charter text, non-truncated)
   - 2: Active drafts (latest 10 active drafts with identifier/title/status)
   - 3: Draft discussions in a WG (last 3 months summary)
5. After every action, return to WG feature menu.
6. Navigation is explicit at all levels:
   - `b` -> go back to previous menu
   - `q` -> quit application

Prompt contract details:
- Top menu only displays user types `1` and `2`.
- Type A prompt is exactly `What technology area are you interested in?`
- Type A selection prompt is `Select 1-<n> to continue with a WG:`
- Back/quit hints are not repeated in every prompt text; navigation tokens still work.

## Parsing/Backend Calls
- Technology matching: `suggest_wgs_by_technology(..., require_all_terms=True)`
- WG resolution: `resolve_wg_name(...)`
- Full charter: `get_wg_charter(...)`
- Active drafts: `get_wg_active_drafts(..., limit=10)`
- Discussions summary: `get_wg_discussion_summary(..., window_days=90)`

## Error Handling
- Invalid selection or empty input prints guidance and keeps user in current step.
- Datatracker/mailarchive errors are shown to the user without crashing the loop.
- Cancel/quit behavior is deterministic via navigation tokens (`b`, `q`).
