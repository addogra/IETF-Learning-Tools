
# New Engineer Quickstart Flow

## Purpose
Provide a compact entrypoint for developer onboarding and point to the full onboarding source.

## Primary Onboarding Source

Use this as canonical guide:
- `docs/product-specs/new-user-onboarding.md`

This document is the short version and should remain aligned with that guide.

## Read Order (Day 0)

1. `requirements.txt`
2. `docs/product-specs/new-user-onboarding.md`
3. `ARCHITECTURE.md`
4. `AGENTS.md`
5. `Lessons.md`
6. `coding_practices.md`
7. `docs/DESIGN.md`
8. `docs/design-docs/index.md`
9. `docs/exec-plans/completed/2026-03-01-req-feat-001-005-docs-sync.md`
10. `docs/exec-plans/tech-debt-tracker.md`

## First Local Run

1. Install with `./scripts/setup.sh` (or platform equivalent).
2. Activate virtual environment.
3. Run CLI: `ietf-wg-agent`.
4. Run tests: `python -m pytest -q tests`.

## Architecture-at-a-Glance

```mermaid
flowchart LR
  CLI[CLI] --> Core[ietf.py]
  MCP[MCP] --> Core
  Daily[Daily + Scheduler] --> Core
  Core --> Sum[summarizer.py]
  Daily --> Notify[notifier.py]
  Daily --> Subs[subscriptions.py]
  Core --> DT[Datatracker]
  Core --> MA[Mailarchive]
```

PlantUML architecture artifact for onboarding slice:
- `docs/design-docs/diagrams/req-feat-001-005-architecture.puml`
- `docs/design-docs/diagrams/req-feat-001-005-architecture.svg`

## Contribution Flow

1. Pick requirement-linked task from active plan/tech debt.
2. Add parser + orchestration changes.
3. Add tests (CLI-path + parser/unit).
4. Run full tests.
5. Update docs and execution-plan files.
6. Update PlantUML source/render artifacts for flow/architecture changes.
7. Update `Lessons.md` and `coding_practices.md` when impacted.
8. Submit PR with requirement IDs and risk notes.
