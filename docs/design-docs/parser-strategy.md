
# Parser Strategy

## Principles
- Prefer explicit section headings when available (`Abstract`, `Status`, `Charter`).
- Use structured table-cell extraction first, then text-pattern fallback.
- Return informative placeholders when data is unavailable.
- Keep parser decisions deterministic (same input shape => same output shape).

## Error Handling
- Wrap network errors in domain-specific errors.
- Preserve partial output when some fields fail (e.g., abstract missing but status present).

## Implementation Pattern

1. API-first retrieval.
2. HTML parse fallback when API is unavailable or incomplete.
3. Field-level fallback extraction before declaring missing values.
4. Output normalization with explicit placeholders.

## Test Expectations

- Parser updates should include unit tests for:
  - normal layout path,
  - fallback layout path,
  - missing-field path.
- Prioritize fixture-backed tests for production-like HTML/API payloads.
