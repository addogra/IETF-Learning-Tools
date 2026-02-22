Author: Aditya Dogra

# Skill: wg-resolution

## Purpose
Resolve user-supplied WG acronym/full-name into a canonical WG and provide relevant suggestions on typos.

## Inputs
- User query string (acronym or full name)
- WG catalog from Datatracker

## Steps
1. Normalize input and candidate WG names/acronyms.
2. Attempt exact acronym/name match.
3. Attempt prefix/contains match.
4. If unresolved, score nearest suggestions by acronym/name similarity.
5. Return top relevant candidates only.

## Outputs
- Resolved WG `{acronym, name}` or
- Ordered suggestions list for disambiguation

## Failure Handling
- If Datatracker catalog fetch fails, return domain error.
- If no relevant candidates exist, return explicit "No WG found".

## Test Coverage
- `tests/test_ietf_suggestions.py`
- `tests/test_cli.py::test_cli_suggestion_selection_flow`
