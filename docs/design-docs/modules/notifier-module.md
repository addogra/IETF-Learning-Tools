Author: Aditya Dogra

# Notifier Module (`src/ietf_wg_agent/notifier.py`)

## Purpose
SMTP email delivery with safe defaults, multipart formatting, and retry logic.

## Control Flow
1. Load SMTP config from env with defaults.
2. Build plain text + HTML multipart message.
3. Attempt send using SMTP or SMTP_SSL.
4. On failure, retry with exponential backoff + jitter.
5. Raise final exception if all retries fail.

## HTML Formatting
- Splits report by WG sections.
- Renders compact cards with WG page links.
- Escapes HTML content to prevent rendering breakage.
