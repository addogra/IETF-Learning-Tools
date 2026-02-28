
# New Engineer Quickstart Flow

## Goal
Get a new engineer productive on `ietf-wg-agent` in one page: understand structure, run locally, validate behavior, and ship safe updates.

## 1) 10-Minute Orientation
```text
+-----------------------------+
| Read in this order          |
+-----------------------------+
| 1. docs/DESIGN.md           |
| 2. ARCHITECTURE.md          |
| 3. docs/design-docs/index.md|
| 4. SKILLS.md                |
| 5. tests/ (feature coverage)|
+-----------------------------+
```

## 2) Repository Map
```text
ietf-wg-agent/
|
+-- src/ietf_wg_agent/
|   +-- ietf.py                 # fetch/parse IETF + mailarchive data
|   +-- cli.py                  # interactive app
|   +-- server.py               # MCP tools
|   +-- daily.py                # daily report/email pipelines
|   +-- discussion_scheduler.py # daily update scheduler loop
|   +-- notifier.py             # SMTP + retry/backoff/jitter + HTML email
|   +-- subscriptions.py        # local JSON subscriptions
|   +-- summarizer.py           # deterministic summarization helpers
|
+-- docs/
|   +-- DESIGN.md
|   +-- design-docs/
|   +-- product-specs/
|
+-- skills/                     # feature skill contracts
+-- tests/                      # parser, CLI, MCP, delivery, docs tests
```

## 3) Runtime Surfaces
```text
User/Automation
   |
   +--> ietf-wg-agent                    (CLI)
   +--> ietf-wg-mcp                      (MCP tools)
   +--> ietf-wg-daily                    (batch daily email/report)
   +--> ietf-wg-daily-updates*           (discussion daily updates)
```

## 4) Feature-to-Flow Snapshot
```text
[WG input]
   |
   v
[Resolve WG in ietf.py]
   |
   +--> [Summary of WG] ----------------> charter parse -> summarize
   +--> [Active drafts] ----------------> docs page -> top 5 -> status+abstract
   +--> [Draft discussions] ------------> mailarchive (3 months) -> summarize
   +--> [Last 2 meetings updates] ------> meetings page -> agenda+minutes
   +--> [Daily updates] ----------------> mailarchive (1 day) -> send only if updates
   +--> [Upcoming IETF agenda] ---------> next meeting -> WG agendas where published
   +--> [Last IETF meeting summary] ----> last meeting -> WG minutes summary
```

## 5) Local Run Quickstart
```text
1. Create venv with Python 3.9+
2. Install package:
   pip install -e .
3. Run CLI:
   ietf-wg-agent
4. Run tests:
   pytest -q
```

## 6) Safe Change Workflow
```text
[Pick feature/module]
   |
   v
[Add/adjust parser or orchestration]
   |
   v
[Add/adjust tests first for new HTML/layout cases]
   |
   v
[Run full test suite: pytest -q]
   |
   v
[Update docs + skills contracts]
   |
   v
[Ship]
```

## 7) Done Criteria Checklist
```text
[ ] Feature works in CLI
[ ] Feature exposed in MCP (if applicable)
[ ] Email/delivery path updated (if applicable)
[ ] New tests added and all tests passing
[ ] docs/DESIGN.md updated
[ ] docs/design-docs/* updated
[ ] SKILLS.md + skills/<feature>/SKILL.md updated
```
