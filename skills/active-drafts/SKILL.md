Author: Aditya Dogra

# Skill: active-drafts

## Purpose
Return top 5 WG drafts from documents page with title, status, URL, and abstract.

## Inputs
- WG acronym
- WG documents page
- Draft detail page
- Datatracker doc API fallback

## Steps
1. Fetch `/wg/<acronym>/documents/`.
2. Parse top draft rows and draft URLs.
3. Extract title/status from row text/cells.
4. Fetch draft page and extract abstract/status fallback.
5. Query doc API fallback for missing title/abstract.
6. Return top 5 normalized `DraftInfo` records.
7. Do not prompt for daily update registration in this flow.

## Outputs
- Ordered list of top draft records

## Failure Handling
- If documents page fails, return domain fetch error.
- If status/abstract missing, return explicit placeholder text.

## Test Coverage
- `tests/test_ietf_drafts.py`
- `tests/test_cli.py::test_cli_option_2_recent_activity_flow`
