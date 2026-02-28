
# Subscriptions Module (`src/ietf_wg_agent/subscriptions.py`)

## Purpose
Store and retrieve daily update subscriptions in a local JSON file.

## Control Flow
1. Load DB file or initialize default structure.
2. Register operation normalizes acronym and deduplicates entries.
3. List operation flattens data into `Subscription` records.
