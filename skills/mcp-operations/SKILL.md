
# Skill: mcp-operations

## Purpose
Expose all core workflows as MCP tools with behavior parity to CLI.

## Inputs
- Tool query parameters
- Core module functions (`ietf`, `summarizer`, `daily`, `subscriptions`)

## Steps
1. Validate MCP runtime availability.
2. Register tool handlers with shared WG resolution logic.
3. Use same suggestion fallback as CLI for unresolved WGs.
4. Return plain text payloads for clients.
5. Keep registration as an explicit tool call (not part of summary responses).

## Outputs
- Registered MCP toolset and text responses

Current toolset includes:
- WG lookup and summary
- Active drafts
- Draft discussions summary
- Updates from last 2 IETF meetings
- Daily updates summary (last 1 day)
- Daily updates send-now trigger
- Upcoming IETF agenda summary
- Last IETF meeting summary
- Daily summary and delivery triggers

## Failure Handling
- If MCP package is missing, raise explicit runtime guidance.
- If query cannot resolve WG, return suggestion list or no-match message.

## Test Coverage
- `tests/test_server_mcp.py`
