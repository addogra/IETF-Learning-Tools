
# SKILLS.md

This repository provides skill-oriented operating guides for core application capabilities.
Each skill is documented in its own `SKILL.md` file.

## Skill Registry

| Skill | Path | Scope |
|---|---|---|
| `wg-resolution` | `skills/wg-resolution/SKILL.md` | WG name/acronym resolution with disambiguation |
| `wg-summary` | `skills/wg-summary/SKILL.md` | WG charter fetch + summary |
| `active-drafts` | `skills/active-drafts/SKILL.md` | Top 5 drafts with status + abstract |
| `wg-discussions` | `skills/wg-discussions/SKILL.md` | Mailarchive discussion summary (last 3 months) |
| `meeting-updates` | `skills/meeting-updates/SKILL.md` | Last 2 meeting agendas and minutes |
| `daily-updates` | `skills/daily-updates/SKILL.md` | Last-day discussion summary + scheduler/email update mode |
| `upcoming-agenda` | `skills/upcoming-agenda/SKILL.md` | Next IETF meeting and summarized WG agendas |
| `last-meeting-summary` | `skills/last-meeting-summary/SKILL.md` | Last completed IETF meeting WG minutes summaries |
| `daily-delivery` | `skills/daily-delivery/SKILL.md` | Daily subscription report + email delivery |
| `mcp-operations` | `skills/mcp-operations/SKILL.md` | MCP tool usage and expected outputs |

## Requirements for every Skill
Each `SKILL.md` must include these sections:
- `## Purpose`
- `## Inputs`
- `## Steps`
- `## Outputs`
- `## Failure Handling`
- `## Test Coverage`

## Maintenance Rules
- Update skill docs whenever behavior changes.
- Add/adjust tests that validate skill registry correctness.
- Keep skill docs aligned with `ARCHITECTURE.md` and `docs/DESIGN.md`.
