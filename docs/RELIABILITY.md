
# RELIABILITY

## Reliability Objectives

1. No silent failure for user-visible operations.
2. Deterministic parsing with graceful fallback paths.
3. Retry-safe outbound notifications.
4. Skip outbound daily discussion updates when no new content exists.

## Implemented Controls

- SMTP send retry with exponential backoff + jitter (`notifier.py`).
- API-first data retrieval with HTML fallback strategies (`ietf.py`).
- Explicit placeholder/error text when fields are unavailable.
- Discussion-update email suppression when last-day activity is empty.

## Known Reliability Risks

- Mailarchive pagination depth is bounded and may under-sample deep history.
- Parser tests rely heavily on synthetic snippets; limited captured-fixture regression corpus.
- Some feature paths return links without rich summary text where requirement expects both.

## Operational Practices

- Run `python -m pytest -q tests` before merge.
- Add fixture-backed parser tests whenever source HTML shape changes.
- Record regressions and mitigations in `docs/exec-plans/tech-debt-tracker.md`.
