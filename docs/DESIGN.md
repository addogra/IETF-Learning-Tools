
# DESIGN

## 1. Purpose
This document explains the complete design of `ietf-wg-agent` so a new engineer can:
- understand what the system does,
- understand each user-facing feature,
- follow control flow through CLI, MCP, and scheduled delivery modes,
- safely extend functionality without breaking existing behavior.

## 2. System Scope
The application helps users monitor IETF Working Groups (WGs) by collecting and summarizing:
- WG charter summary,
- active drafts (top 5 with abstract + status),
- WG discussion summaries (last 3 months),
- updates from last 2 IETF meetings (agenda + minutes),
- daily updates (last day mailarchive activity, send only if activity exists),
- agenda of upcoming IETF meeting,
- summary of last IETF meeting.

## 3. Runtime Surfaces
- CLI app: `ietf-wg-agent`
- MCP server: `ietf-wg-mcp`
- Batch daily runner: `ietf-wg-daily`
- Daily discussion scheduler:
  - `ietf-wg-daily-updates`
  - `ietf-wg-daily-updates-scheduler`

## 3.1 Python Version Contract
- Entire project baseline: Python 3.9+
- MCP runtime contract: Python 3.10+
- Bootstrap behavior when MCP is requested from Python 3.9:
  - auto-detect Python 3.10+ interpreter on PATH,
  - create/use `.venv-mcp` by default,
  - provide OS-specific install guidance if no compatible interpreter exists.

## 4. High-Level Architecture (ASCII)
```text
                         +----------------------------------+
                         |          User / Caller           |
                         |  CLI user or MCP client or cron  |
                         +----------------+-----------------+
                                          |
               +--------------------------+--------------------------+
               |                                                     |
     +---------v---------+                                 +---------v---------+
     | CLI (cli.py)      |                                 | MCP (server.py)   |
     | interactive menus |                                 | tool endpoints    |
     +---------+---------+                                 +---------+---------+
               |                                                     |
               +--------------------------+--------------------------+
                                          |
                                 +--------v---------+
                                 | Core IETF Layer  |
                                 |    (ietf.py)     |
                                 | parsing + lookup |
                                 +----+---------+---+
                                      |         |
                           +----------+         +--------------------+
                           |                                   |
                   +-------v--------+                  +-------v--------+
                   | summarizer.py  |                  | subscriptions  |
                   | deterministic  |                  | + notifier +   |
                   | summaries      |                  | daily pipeline |
                   +-------+--------+                  +-------+--------+
                           |                                   |
                           +-------------------+---------------+
                                               |
                                       +-------v--------+
                                       | Output Channels|
                                       | console / MCP  |
                                       | text / email   |
                                       +----------------+
```

## 5. External Integrations
```text
+---------------------------------------------------------------+
|                       External Sources                        |
+-----------------------------+---------------------------------+
| datatracker.ietf.org        | WG metadata, about, documents, |
|                             | meetings, draft detail pages    |
+-----------------------------+---------------------------------+
| mailarchive.ietf.org        | WG discussion threads           |
+-----------------------------+---------------------------------+
| SMTP server                 | Email delivery                  |
+-----------------------------+---------------------------------+
```

## 6. End-to-End Functional Flow (ASCII)
```text
[Start]
   |
   v
[Read Email]
   |
   v
[Read WG Input]
   |
   v
[Resolve WG from acronym/full name]
   |
   +--> exact match --------------------+
   |                                    |
   +--> no exact match -> [Top relevant suggestions] -> [User select/cancel]
                                             |
                                             v
                                      [WG selected?]
                                             |
                                             +--> no -> [Exit]
                                             |
                                             +--> yes
                                                   |
                                                   v
                                      [Optional subscription register]
                                                   |
                                                   v
                                         [Choose feature option]
                                                   |
      +----------------------+--------------------+-----------------------+
      |                      |                    |                       |
      v                      v                    v                       v
[WG Summary]         [Active Drafts]     [Draft Discussions]    [Meeting Updates...]
      |                      |                    |                       |
      v                      v                    v                       v
[Render to CLI/MCP]  [Render to CLI/MCP] [Render to CLI/MCP]   [Render to CLI/MCP]
```

## 7. Feature Design (All User Features)
### 7.1 WG Resolution and Suggestions
- Accepts acronym or full name.
- Matching strategy:
  - exact acronym match,
  - exact name match,
  - normalized partial/keyword match,
  - relevance-filtered typo suggestions.
- Suggestion behavior is bounded and avoids unrelated WGs.

### 7.2 Summary of WG
- Source: `https://datatracker.ietf.org/wg/<acronym>/about/`
- Extract charter text and produce concise summary.
- If sections are missing, returns graceful fallback text.

### 7.3 Active Drafts
- Source: `https://datatracker.ietf.org/wg/<acronym>/documents/`
- Picks top 5 draft entries.
- For each draft:
  - title,
  - status (from draft page/document metadata),
  - abstract.
- Parser is defensive to handle changing table layouts.

### 7.4 Draft Discussions in a WG
- Source: `https://mailarchive.ietf.org/arch/browse/<acronym>/`
- Filter window: last 3 months.
- Returns summary of themes + activity signals.

### 7.5 Updates from Last 2 IETF Meetings
- Source: `https://datatracker.ietf.org/wg/<acronym>/meetings/`
- Extract last 2 meeting entries with:
  - agenda link/info,
  - minutes link/info.

### 7.6 Daily Updates
- Source: mailarchive browse for WG.
- Window: last day only.
- Behavior:
  - if activity exists -> summarize and deliver,
  - if no activity -> skip email send.
- Supports ad-hoc run and scheduler mode.

### 7.7 Agenda of Upcoming IETF Meeting
- Find next IETF meeting metadata first (number, dates, location).
- Traverse WG meeting info and include only WGs where agenda is published.
- Skip WGs with no agenda yet.

### 7.8 Summary of Last IETF Meeting
- Find most recent completed IETF meeting.
- Traverse WG meeting records.
- Include only WGs with meeting material/minutes for that meeting.
- Summarize minutes per WG.

## 8. Delivery Modes
```text
+----------------------+-------------------------+------------------------+
| Mode                 | Entry point             | Output                 |
+----------------------+-------------------------+------------------------+
| Interactive          | ietf-wg-agent           | Console text           |
| MCP tools            | ietf-wg-mcp             | MCP tool responses     |
| Batch daily report   | ietf-wg-daily           | Email + report file    |
| Daily discussion run | ietf-wg-daily-updates   | Email/console summary  |
| Continuous schedule  | ...-updates-scheduler   | periodic daily checks  |
+----------------------+-------------------------+------------------------+
```

## 9. Module Responsibilities
### `src/ietf_wg_agent/ietf.py`
- All remote data retrieval and HTML/API parsing.
- WG lookup, suggestions, charter extraction, drafts parsing, discussions parsing, meetings parsing.

### `src/ietf_wg_agent/summarizer.py`
- Deterministic summarization helpers for charter/discussion/minutes style text.

### `src/ietf_wg_agent/cli.py`
- User prompts, menu routing, display formatting, suggestion interaction.

### `src/ietf_wg_agent/server.py`
- MCP tool registration and thin orchestration wrappers around core functions.

### `src/ietf_wg_agent/subscriptions.py`
- JSON-based subscription persistence (`~/.ietf_wg_agent_subscriptions.json`).

### `src/ietf_wg_agent/notifier.py`
- SMTP sending logic, compact HTML email generation, retry/backoff with jitter.

### `src/ietf_wg_agent/daily.py`
- Daily pipelines: load subscriptions, gather summaries, send emails, write daily reports.

### `src/ietf_wg_agent/discussion_scheduler.py`
- Time-loop scheduler for periodic “daily updates” checks.

## 10. Detailed Architecture Flow (ASCII)
```text
[Request arrives]
   |
   +--> CLI route ------------------------------+
   |                                            |
   +--> MCP tool route ----------------------+  |
                                              |  |
                                              v  v
                                     [Resolve WG / validate inputs]
                                              |
                                              v
                                      [Call ietf.py operation]
                                              |
                         +--------------------+---------------------+
                         |                                          |
                         v                                          v
               [Raw structured data]                        [Errors/timeouts]
                         |                                          |
                         v                                          v
                 [summarizer.py if needed]                [fallback message]
                         |
                         +--------------------+---------------------+
                                              |
                                              v
                                   [Delivery formatter]
                                              |
                         +--------------------+---------------------+
                         |                                          |
                         v                                          v
                [console or MCP text]                    [daily email sender]
```

## 11. Reliability and Failure Handling
- Network failures are caught and surfaced with user-readable errors.
- Parsers use fallback selectors; missing fields return explicit placeholders.
- Email delivery uses retries with exponential backoff + random jitter.
- Daily-updates email is suppressed when no new discussion activity exists.
- WG typo input uses constrained suggestions to reduce irrelevant prompts.

## 12. Data and Persistence
- Subscription store: `~/.ietf_wg_agent_subscriptions.json`
- Daily report artifact: `reports/daily-YYYY-MM-DD.txt`
- No server-side database required; design remains portable across OSes.

## 13. Test Strategy
- Unit tests for parsers (draft titles/status/abstract, discussions, meetings).
- CLI flow tests for option routing and suggestion handling.
- MCP tests for tool registration and route execution.
- Daily delivery/scheduler tests for “send only when updates exist”.
- Documentation/skills contract tests to prevent docs-to-code drift.

## 14. Extension Guidance for New Contributors
When adding a feature:
1. Implement parser/retrieval in `ietf.py`.
2. Add route in CLI and MCP (if exposed).
3. Add/update email delivery behavior when relevant.
4. Add tests first for HTML variants and fallback paths.
5. Update:
   - `docs/DESIGN.md` (this file),
   - `docs/design-docs/*`,
   - product spec docs,
   - `SKILLS.md` and feature `skills/*/SKILL.md`.
