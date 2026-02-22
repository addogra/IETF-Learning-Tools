Author: Aditya Dogra

# Parser Strategy

## Principles
- Prefer explicit section headings when available (`Abstract`, `Status`, `Charter`).
- Use structured table-cell extraction first, then text-pattern fallback.
- Return informative placeholders when data is unavailable.

## Error Handling
- Wrap network errors in domain-specific errors.
- Preserve partial output when some fields fail (e.g., abstract missing but status present).
