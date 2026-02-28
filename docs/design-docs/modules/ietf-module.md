
# IETF Data Module (`src/ietf_wg_agent/ietf.py`)

## Purpose
Centralized integration layer for external IETF sources and resilient parsing.

## Main Sections
- WG catalog + resolution + suggestions
- Charter extraction
- Legacy milestones/RFC helpers (kept for compatibility)
- Draft extraction from WG documents page
- Draft detail parsing (title/status/abstract)
- Discussion extraction from mailarchive
- Meeting updates extraction from WG meetings page
- Last-day discussion extraction for daily-update mode
- Upcoming IETF agenda extraction across WG meeting pages
- Last completed IETF meeting summary extraction from WG minutes

## Draft Flow
1. Fetch `wg/<acronym>/documents/`.
2. Parse draft rows and draft document URLs.
3. Parse title/status from row text/cells.
4. Fetch each draft doc page for abstract/status fallback.
5. Query Datatracker doc API fallback for title/abstract if needed.
6. Return normalized `DraftInfo` list.

## Discussion Flow
1. Fetch `mailarchive ... /arch/browse/<acronym>/`.
2. Parse thread links, date/time, author metadata.
3. Filter by time window (last N months).
4. Follow older-page links (bounded pages).
5. Return reverse-chronological deduplicated posts.

## Meeting Updates Flow
1. Fetch `wg/<acronym>/meetings/`.
2. Parse agenda/minutes links.
3. Group links by inferred meeting label (IETF number/date).
4. Return latest 2 meetings with agenda/minutes URLs.

## Reliability Features
- API-first with HTML fallback.
- Multiple parsing strategies per field.
- Placeholder strings for partial data.
