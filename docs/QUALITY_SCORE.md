
# QUALITY SCORE

## Baseline Gates

1. All tests pass:
   - `python -m pytest -q tests`
2. Behavioral changes include:
   - at least one CLI-path test,
   - at least one parser/unit test.
3. Documentation updates included for any behavior/interface/data-source change.
4. Execution plans updated:
   - active plan state,
   - completed work archive,
   - tech debt deltas.

## Current Coverage Summary (As-Coded)

Strong coverage:
- CLI routing flows.
- Draft parsing/status/abstract extraction.
- Discussion parsing and summary rendering.
- Upcoming/last meeting aggregation paths.
- MCP tool registration.
- Daily delivery skip-if-no-updates behavior.

Coverage gaps to improve:
- Captured HTML fixture contract tests.
- Deeper technology-onboarding/vector DB ranking quality tests (current path implemented; needs richer fixture coverage).
- Draft tracker tests (feature not yet implemented).
- Webex-mode parity tests (mode not yet implemented).

## Scoring Lens (Team Use)

- `A`: requirement covered + tests + docs + delivery parity.
- `B`: requirement covered + tests, minor docs/parity gaps.
- `C`: partial implementation or weak edge-case coverage.
- `D`: planned only, not yet coded.
