# Author: Aditya Dogra
from __future__ import annotations

"""Deterministic text summarization helpers.

Control flow:
1) Normalize and tokenize text.
2) Compute lightweight relevance signals (keywords/frequency).
3) Produce structured summaries for CLI/MCP/email output.
"""

import re
from typing import Optional, Sequence

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "in", "is", "it", "its", "of", "on", "or", "that", "the", "their", "to",
    "this", "these", "those", "will", "with", "working", "group", "ietf",
}


def _split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []
    parts = re.split(r"(?<=[.!?])\s+", compact)
    return [p.strip() for p in parts if len(p.strip()) > 35]


def _keywords(text: str, limit: int = 6) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9-]+", text.lower())
    freq: dict[str, int] = {}
    for word in words:
        if len(word) < 4 or word in STOPWORDS:
            continue
        freq[word] = freq.get(word, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in ranked[:limit]]


def summarize_charter(charter_text: str, max_sentences: int = 4) -> str:
    """Create a lightweight summary from charter text.

    Flow: sentence extraction -> keyword ranking -> bullet rendering.
    """
    sentences = _split_sentences(charter_text)
    if not sentences:
        return "No usable charter text was found to summarize."

    selected = sentences[:max_sentences]
    keys = _keywords(charter_text)

    lines = ["WG charter summary:"]
    for sentence in selected:
        lines.append(f"- {sentence}")
    if keys:
        lines.append(f"- Key topics: {', '.join(keys)}")

    return "\n".join(lines)


def summarize_discussions(
    posts: Sequence[object],
    months: int = 3,
    max_subjects: int = 5,
    period_label: Optional[str] = None,
) -> str:
    """Summarize WG draft discussions over the most recent period.

    Flow: collect metadata -> aggregate topics/authors -> render summary.
    """
    label = period_label or f"last {months} months"
    if not posts:
        return f"No discussion posts found in the {label}."

    subjects: list[str] = []
    authors: list[str] = []
    for post in posts:
        subject = getattr(post, "subject", "").strip()
        author = getattr(post, "author", "").strip()
        if subject:
            subjects.append(subject)
        if author and author.lower() != "unknown author":
            authors.append(author)

    top_keywords = _keywords(" ".join(subjects), limit=6)
    author_freq: dict[str, int] = {}
    for author in authors:
        author_freq[author] = author_freq.get(author, 0) + 1
    top_authors = sorted(author_freq.items(), key=lambda x: (-x[1], x[0]))[:3]

    lines = [f"Draft discussions summary ({label}):"]
    lines.append(f"- Total discussion posts: {len(posts)}")
    if top_keywords:
        lines.append(f"- Frequent topics: {', '.join(top_keywords)}")
    if top_authors:
        lines.append(
            "- Most active participants: "
            + ", ".join(f"{name} ({count})" for name, count in top_authors)
        )

    lines.append("- Recent discussion threads:")
    for post in posts[:max_subjects]:
        subject = getattr(post, "subject", "(no subject)")
        date = getattr(post, "date", "Unknown date")
        url = getattr(post, "url", "")
        lines.append(f"- {subject} [{date}]")
        if url:
            lines.append(f"  {url}")

    return "\n".join(lines)
