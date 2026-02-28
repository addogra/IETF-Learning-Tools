
# Design Docs Index

## Purpose
This folder is the implementation design source-of-truth for maintainers and agents.
Use it before changing parsing logic, runtime flows, or module interfaces.

## Runtime Compatibility Contract
- Base runtime compatibility: Python 3.9+
- MCP runtime compatibility: Python 3.10+
- CI validates compatibility for Python 3.9/3.10/3.11/3.12.
- MCP install path is validated separately on Python 3.10+.

## Recommended Reading Order
1. `../product-specs/new-user-onboarding.md`
2. `core-beliefs.md`
3. `../DESIGN.md`
4. `data-sources.md`
5. `parser-strategy.md`
6. Module docs in `modules/`

## Core Design Docs
- `../product-specs/new-user-onboarding.md`: complete Day-0 to PR developer onboarding.
- `core-beliefs.md`: non-negotiable design principles.
- `data-sources.md`: source endpoints and fallback rules.
- `parser-strategy.md`: parsing approach and expected failure modes.
- `../DESIGN.md`: system-level architecture + flowcharts.
- `../../SKILLS.md`: skill registry for feature-level operational contracts.

## Module Design Docs
- `modules/cli-module.md`: CLI implementation and control flow.
- `modules/ietf-module.md`: IETF data/parsing implementation and control flow.
- `modules/summarizer-module.md`: summary generation implementation and control flow.
- `modules/subscriptions-module.md`: persistence implementation and control flow.
- `modules/notifier-module.md`: SMTP delivery implementation and control flow.
- `modules/daily-module.md`: scheduled report/email run implementation and control flow.
- `modules/server-module.md`: MCP tool orchestration implementation and control flow.

## Feature-to-Module Map
- WG resolution + suggestions: `modules/ietf-module.md`, `modules/cli-module.md`
- Charter summary: `modules/ietf-module.md`, `modules/summarizer-module.md`
- Active drafts (title/status/abstract): `modules/ietf-module.md`, `modules/cli-module.md`
- Draft discussions summary: `modules/ietf-module.md`, `modules/summarizer-module.md`
- Meeting updates (agenda/minutes): `modules/ietf-module.md`, `modules/cli-module.md`
- Daily updates (last-day discussions + scheduler): `modules/ietf-module.md`, `modules/cli-module.md`, `modules/daily-module.md`
- Upcoming IETF agenda (next meeting + WG agendas): `modules/ietf-module.md`, `modules/cli-module.md`, `modules/daily-module.md`
- Last IETF meeting summary (WG minutes): `modules/ietf-module.md`, `modules/cli-module.md`, `modules/daily-module.md`
- Daily email delivery: `modules/daily-module.md`, `modules/notifier-module.md`
- MCP tools: `modules/server-module.md`

## Update Rules
- Any behavior change must update the relevant module doc.
- If data-source assumptions change, update `data-sources.md` and `parser-strategy.md`.
- Keep `../DESIGN.md` aligned with actual runtime flow and options.
