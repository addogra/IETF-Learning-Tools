
# Skill: wg-discussions

## Purpose
Summarize draft discussions from WG mailarchive over the last 3 months.

## Inputs
- WG acronym
- Mailarchive browse pages

## Steps
1. Fetch `mailarchive ... /arch/browse/<acronym>/`.
2. Parse thread links, dates, authors.
3. Filter posts by 3-month cutoff.
4. Follow older-page links with bounded pagination.
5. Summarize topics/authors and list recent threads.
6. Do not prompt for daily update registration in this flow.

## Outputs
- Discussion summary including totals, topics, active authors, and thread links

## Failure Handling
- If mailarchive fetch fails, return domain fetch error.
- If no posts in window, return explicit empty-summary message.

## Test Coverage
- `tests/test_ietf_discussions.py`
- `tests/test_cli.py::test_cli_option_3_discussions_flow`
