
# MCP Server Module (`src/ietf_wg_agent/server.py`)

## Purpose
Expose CLI-equivalent capabilities as MCP tools.

## Control Flow
1. Resolve WG for each incoming query.
2. If unresolved, return deterministic suggestions.
3. Delegate to core data/summarizer modules.
4. For `summary_of_wg`, return complete charter text (REQ-FEAT-003 contract alignment).
5. Support daily update operations (last-day summary and send-now path).
6. Support IETF meeting-oriented tools (upcoming agenda and last meeting summary).
7. Format REQ-FEAT-006 output with explicit `Agendas` and `Minutes` sections.
8. Return plain text payload for MCP clients.

## Stability Rule
- MCP tools should mirror CLI behavior to avoid divergent outcomes.
