# Author: Aditya Dogra
"""IETF WG agent package."""

from __future__ import annotations

import warnings

# Hide noisy urllib3 LibreSSL warning on older Python/macOS runtimes.
try:
    from urllib3.exceptions import NotOpenSSLWarning

    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except Exception:
    warnings.filterwarnings(
        "ignore",
        message="urllib3 v2 only supports OpenSSL 1.1.1+",
    )

__all__ = [
    "ietf",
    "summarizer",
    "subscriptions",
]
