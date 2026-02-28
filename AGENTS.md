
# AGENTS.md

## Mission
Build and maintain an IETF WG assistant that reliably resolves WG names, summarizes charter/discussions, extracts draft status/abstracts, and supports daily email updates.

## How Agents Should Work In This Repo
- Read `ARCHITECTURE.md` before major changes.
- Keep implementation and tests aligned. Any behavioral change must include tests.
- Prefer deterministic parsing and graceful fallback paths for external HTML/API changes.
- Do not weaken existing CLI or MCP behaviors without explicit migration notes.

## Mandatory Update Checklist
- Update docs under `docs/` when behavior, data sources, or interfaces change.
- Run `python -m pytest -q tests` before finalizing.
- If adding a new user-facing feature, add at least one CLI-path test and one parser/unit test.

## Source-of-Truth Files
- Runtime architecture: `ARCHITECTURE.md`
- Product scope: `docs/product-specs/index.md`
- Active execution plans: `docs/exec-plans/active/`
- Quality and safety standards: `docs/QUALITY_SCORE.md`, `docs/RELIABILITY.md`, `docs/SECURITY.md`
