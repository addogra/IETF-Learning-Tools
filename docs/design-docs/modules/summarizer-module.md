
# Summarizer Module (`src/ietf_wg_agent/summarizer.py`)

## Purpose
Create deterministic lightweight summaries from text/content lists.

## Control Flow
- Charter summary:
  1. Sentence splitting
  2. Keyword extraction
  3. Structured bullet output

- Discussion summary:
  1. Collect subjects/authors
  2. Compute frequency and topic keywords
  3. Render period summary with recent threads
