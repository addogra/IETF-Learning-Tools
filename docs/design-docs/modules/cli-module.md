Author: Aditya Dogra

# CLI Module (`src/ietf_wg_agent/cli.py`)

## Purpose
Provide interactive user flow for WG operations.

## Control Flow
1. Validate user email input.
2. Resolve WG from user input.
3. If no match, run suggestion flow and let user disambiguate.
4. Dispatch menu option:
   - 1: Charter summary
   - 2: Active drafts (top 5 + status + abstract)
   - 3: Draft discussions summary (last 3 months)
   - 4: Updates from last 2 meetings (agenda + minutes)
   - 5: Daily updates summary (last 1 day) + optional scheduler start
   - 6: Upcoming IETF agenda summary (next meeting)
   - 7: Last IETF meeting summary (WG minutes)
5. If option is 3-7 and email provided, optionally register daily updates.
6. Print formatted result.

## Error Handling
- Invalid email -> immediate user-facing validation message.
- Datatracker/mailarchive errors -> caught and shown as domain errors.
- Invalid suggestion index/empty selection -> clean cancel/exit.
