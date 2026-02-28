
# Core Beliefs

Build every capability as a single deterministic domain workflow with graceful
degradation, then expose that same workflow consistently across CLI,
webex-bot, MCP, and daily automation.

## Practical Form

1. Put business logic in core modules (`ietf.py`, `summarizer.py`, `daily.py`), not interface layers.
2. Use API-first extraction with robust HTML fallbacks.
3. Return partial useful output on failures (never all-or-nothing unless truly unrecoverable).
4. Keep output contracts stable and typed (dataclass models) so new features compose cleanly.
5. Enforce parity: same WG resolution, parsing, and summaries across CLI, MCP, and scheduled delivery.
6. Treat tests as interface contracts: each feature needs parser/unit coverage plus user-path coverage (CLI and MCP where relevant).

## One-Line Version

One domain pipeline, many surfaces, deterministic behavior, graceful fallback,
test-locked contracts.
