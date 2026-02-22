# Author: Aditya Dogra
from __future__ import annotations

"""IETF source integration and parsing layer.

Control-flow sections in this module:
1) WG discovery and query resolution.
2) Charter extraction from WG pages.
3) Draft extraction/status/abstract enrichment.
4) Discussion extraction from mailarchive over a time window.

Each section uses API-first + HTML fallback parsing to resist layout changes.
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
from datetime import date as date_cls, datetime, timedelta, timezone
import re
from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup

WG_API_URL = "https://datatracker.ietf.org/api/v1/group/group/"
WG_ABOUT_URL_TEMPLATE = "https://datatracker.ietf.org/wg/{acronym}/about/"
WG_DOCUMENTS_URL_TEMPLATE = "https://datatracker.ietf.org/wg/{acronym}/documents/"
MILESTONE_API_URL = "https://datatracker.ietf.org/api/v1/group/milestone/"
DOC_API_URL = "https://datatracker.ietf.org/api/v1/doc/document/"
MAILARCHIVE_BROWSE_URL_TEMPLATE = "https://mailarchive.ietf.org/arch/browse/{acronym}/"
WG_MEETINGS_URL_TEMPLATE = "https://datatracker.ietf.org/wg/{acronym}/meetings/"
MEETINGS_INDEX_URL = "https://datatracker.ietf.org/meeting/"
MEETING_PAGE_URL_TEMPLATE = "https://datatracker.ietf.org/meeting/{number}/"


@dataclass(frozen=True)
class WorkingGroup:
    acronym: str
    name: str


@dataclass(frozen=True)
class ApprovedRFC:
    name: str
    title: str
    time: str
    url: str


@dataclass(frozen=True)
class DraftInfo:
    name: str
    title: str
    status: str
    abstract: str
    url: str


@dataclass(frozen=True)
class DiscussionPost:
    date: str
    subject: str
    author: str
    url: str


@dataclass(frozen=True)
class MeetingUpdate:
    meeting: str
    agendas: list[str]
    minutes: list[str]


@dataclass(frozen=True)
class UpcomingAgendaItem:
    wg_acronym: str
    wg_name: str
    agenda_url: str
    agenda_summary: str


@dataclass(frozen=True)
class LastMeetingItem:
    wg_acronym: str
    wg_name: str
    agenda_url: str
    minutes_url: str
    minutes_summary: str


class DatatrackerError(RuntimeError):
    pass


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _normalize_compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower()).strip()


def _tokenize(text: str) -> set[str]:
    return {tok for tok in _normalize(text).split() if len(tok) >= 3}


def fetch_working_groups(timeout: int = 20) -> list[WorkingGroup]:
    """Fetch WG acronym/name catalog from IETF Datatracker API.

    Section 1 entry point for WG discovery.
    """
    params = {"type": "wg", "limit": 1000}
    try:
        response = requests.get(WG_API_URL, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DatatrackerError(f"Unable to fetch WG list: {exc}") from exc

    payload = response.json()
    objects = payload.get("objects", [])

    groups: list[WorkingGroup] = []
    for item in objects:
        acronym = str(item.get("acronym", "")).strip()
        name = str(item.get("name", "")).strip()
        if acronym and name:
            groups.append(WorkingGroup(acronym=acronym, name=name))

    if not groups:
        raise DatatrackerError("No working groups returned by Datatracker API")

    return groups


def resolve_working_group(
    query: str, groups: Iterable[WorkingGroup]
) -> Optional[WorkingGroup]:
    """Resolve acronym or full/partial WG name into a WG object.

    Flow: exact match -> prefix/contains heuristics.
    """
    q = _normalize(query)
    if not q:
        return None

    candidates = list(groups)

    # Strong exact matches first.
    for wg in candidates:
        if _normalize(wg.acronym) == q or _normalize(wg.name) == q:
            return wg

    # Prefix and containment matching.
    starts: list[WorkingGroup] = []
    contains: list[WorkingGroup] = []
    for wg in candidates:
        name = _normalize(wg.name)
        acronym = _normalize(wg.acronym)
        if name.startswith(q) or acronym.startswith(q):
            starts.append(wg)
        elif q in name or q in acronym:
            contains.append(wg)

    if starts:
        return sorted(starts, key=lambda w: len(w.name))[0]
    if contains:
        return sorted(contains, key=lambda w: len(w.name))[0]
    return None


def suggest_working_groups(
    query: str, groups: Iterable[WorkingGroup], limit: int = 5
) -> list[WorkingGroup]:
    """Suggest nearest relevant WGs for misspelled acronym/name input.

    Flow: detect acronym-like vs name-like query, then score/re-rank.
    """
    q = _normalize(query)
    if not q:
        return []

    qc = _normalize_compact(query)
    query_tokens = _tokenize(query)
    is_acronym_like = " " not in q and 2 <= len(qc) <= 10

    scored: list[tuple[float, WorkingGroup]] = []
    for wg in groups:
        name = _normalize(wg.name)
        acronym = _normalize(wg.acronym)
        acronym_compact = _normalize_compact(wg.acronym)

        score = 0.0
        if is_acronym_like:
            if not acronym_compact:
                continue
            ratio = SequenceMatcher(None, qc, acronym_compact).ratio()
            common_chars = len(set(qc) & set(acronym_compact))
            if common_chars < max(2, len(qc) // 2):
                continue

            score = ratio
            if acronym_compact.startswith(qc) or qc.startswith(acronym_compact):
                score += 0.22
            if qc in acronym_compact or acronym_compact in qc:
                score += 0.12

            # Keep suggestions tight for acronym inputs.
            if score < 0.62:
                continue
        else:
            name_tokens = _tokenize(name)
            overlap = len(query_tokens & name_tokens)
            ratio_name = SequenceMatcher(None, q, name).ratio()
            ratio_acronym = SequenceMatcher(None, qc, acronym_compact).ratio()

            if overlap == 0 and ratio_name < 0.62 and ratio_acronym < 0.75:
                continue

            score = overlap * 0.6 + ratio_name * 0.7 + ratio_acronym * 0.4
            if name.startswith(q) or acronym.startswith(q):
                score += 0.2

        scored.append((score, wg))

    scored.sort(key=lambda item: (-item[0], len(item[1].name), item[1].acronym))
    out: list[WorkingGroup] = []
    seen: set[str] = set()
    for _, wg in scored:
        key = wg.acronym.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(wg)
        if len(out) >= limit:
            break
    return out


def fetch_charter_text(acronym: str, timeout: int = 20) -> str:
    """Fetch and extract the WG charter text from the WG about page.

    Section 2 entry point for charter retrieval.
    """
    url = WG_ABOUT_URL_TEMPLATE.format(acronym=acronym.lower())
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DatatrackerError(f"Unable to fetch charter page: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")

    heading = soup.find(
        lambda tag: tag.name in {"h1", "h2", "h3", "h4"}
        and "charter for" in tag.get_text(" ", strip=True).lower()
    )

    if not heading:
        text = soup.get_text("\n", strip=True)
        raise DatatrackerError(
            f"Could not find charter heading at {url}. Page excerpt: {text[:200]}"
        )

    chunks: list[str] = []
    for sibling in heading.next_siblings:
        name = getattr(sibling, "name", None)
        if name in {"h1", "h2", "h3", "h4"}:
            break
        get_text = getattr(sibling, "get_text", None)
        if callable(get_text):
            txt = get_text(" ", strip=True)
            if txt:
                chunks.append(txt)

    charter = "\n".join(chunks).strip()
    if not charter:
        raise DatatrackerError(f"No charter text found at {url}")

    return charter


def _extract_draft_names(text: str) -> list[str]:
    drafts = re.findall(r"draft-[a-z0-9-]+", text.lower())
    seen: set[str] = set()
    out: list[str] = []
    for draft in drafts:
        if draft not in seen:
            seen.add(draft)
            out.append(draft)
    return out


def _parse_datetime(value: str) -> datetime:
    if not value:
        return datetime.min
    clean = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(clean)
    except ValueError:
        return datetime.min


def _get_group_id(acronym: str, timeout: int = 20) -> Optional[int]:
    params = {"type": "wg", "acronym": acronym.lower()}
    try:
        response = requests.get(WG_API_URL, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return None

    for item in payload.get("objects", []):
        if str(item.get("acronym", "")).lower() == acronym.lower():
            group_id = item.get("id")
            if isinstance(group_id, int):
                return group_id
    return None


def _fetch_milestones_from_api(acronym: str, timeout: int = 20) -> list[str]:
    group_id = _get_group_id(acronym, timeout=timeout)
    if group_id is None:
        return []

    params = {"group": group_id, "order_by": "-due"}
    try:
        response = requests.get(MILESTONE_API_URL, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return []

    milestones: list[str] = []
    for item in payload.get("objects", []):
        desc = str(item.get("desc", "")).strip()
        if desc:
            milestones.append(desc)
    return milestones


def _fetch_milestones_from_about_page(acronym: str, timeout: int = 20) -> list[str]:
    url = WG_ABOUT_URL_TEMPLATE.format(acronym=acronym.lower())
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    heading = soup.find(
        lambda tag: tag.name in {"h1", "h2", "h3", "h4"}
        and "milestones" in tag.get_text(" ", strip=True).lower()
    )
    if not heading:
        return []

    milestones: list[str] = []
    for sibling in heading.next_siblings:
        name = getattr(sibling, "name", None)
        if name in {"h1", "h2", "h3", "h4"}:
            break
        get_text = getattr(sibling, "get_text", None)
        if callable(get_text):
            text = get_text(" ", strip=True)
            if text and len(text) > 8:
                milestones.append(text)
    return milestones


def fetch_active_drafts_from_last_two_meetings(
    acronym: str, timeout: int = 20, limit: int = 8
) -> list[str]:
    """Best-effort extraction of active drafts from recent milestone entries."""
    milestones = _fetch_milestones_from_api(acronym, timeout=timeout)
    if not milestones:
        milestones = _fetch_milestones_from_about_page(acronym, timeout=timeout)

    if not milestones:
        return []

    # Approximate "last 2 meetings" with the most recent milestone items.
    candidates = milestones[:12]
    drafts: list[str] = []
    seen: set[str] = set()
    for milestone in candidates:
        for draft in _extract_draft_names(milestone):
            if draft in seen:
                continue
            seen.add(draft)
            drafts.append(draft)
            if len(drafts) >= limit:
                return drafts
    return drafts


def _fetch_approved_rfcs_from_api(
    acronym: str, timeout: int = 20, limit: int = 5
) -> list[ApprovedRFC]:
    group_id = _get_group_id(acronym, timeout=timeout)
    if group_id is None:
        return []

    params = {
        "group": group_id,
        "type": "rfc",
        "order_by": "-time",
        "limit": 200,
    }
    try:
        response = requests.get(DOC_API_URL, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return []

    candidates: list[ApprovedRFC] = []
    for item in payload.get("objects", []):
        name = str(item.get("name", "")).strip()
        title = str(item.get("title", "")).strip()
        state = str(item.get("std_level", "")).lower() + " " + str(
            item.get("states", "")
        ).lower()
        if not name.lower().startswith("rfc"):
            continue
        if "approved" not in state and "published" not in state and "rfc" not in state:
            # Datatracker schemas vary; keep RFC docs while preferring approved/published.
            pass
        time_val = str(item.get("time", "")).strip()
        url = f"https://datatracker.ietf.org/doc/{name.lower()}/"
        candidates.append(
            ApprovedRFC(name=name.upper(), title=title, time=time_val, url=url)
        )

    candidates.sort(key=lambda r: _parse_datetime(r.time), reverse=True)
    return candidates[:limit]


def _fetch_approved_rfcs_from_documents_page(
    acronym: str, timeout: int = 20, limit: int = 5
) -> list[ApprovedRFC]:
    url = WG_DOCUMENTS_URL_TEMPLATE.format(acronym=acronym.lower())
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=re.compile(r"/doc/rfc\d+/?$"))

    out: list[ApprovedRFC] = []
    seen: set[str] = set()
    for link in links:
        href = str(link.get("href", "")).strip()
        text = link.get_text(" ", strip=True)
        if not text:
            continue
        name = text.upper()
        if not name.startswith("RFC"):
            m = re.search(r"rfc\d+", href.lower())
            if not m:
                continue
            name = m.group(0).upper()
        if name in seen:
            continue
        seen.add(name)
        abs_url = "https://datatracker.ietf.org" + href
        out.append(ApprovedRFC(name=name, title="", time="", url=abs_url))
        if len(out) >= limit:
            break
    return out


def fetch_last_approved_rfcs(
    acronym: str, timeout: int = 20, limit: int = 5
) -> list[ApprovedRFC]:
    rfcs = _fetch_approved_rfcs_from_api(acronym, timeout=timeout, limit=limit)
    if rfcs:
        return rfcs
    return _fetch_approved_rfcs_from_documents_page(acronym, timeout=timeout, limit=limit)


def _extract_abstract_from_doc_page(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(
        lambda tag: tag.name in {"h1", "h2", "h3", "h4"}
        and "abstract" in tag.get_text(" ", strip=True).lower()
    )
    if not heading:
        text = soup.get_text("\n", strip=True)
        match = re.search(
            r"\bAbstract\b\s*(.+?)(?:\bStatus of This Memo\b|\bCopyright Notice\b|\bTable of Contents\b|\n\s*1\.)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return ""
        return re.sub(r"\s+", " ", match.group(1)).strip()

    chunks: list[str] = []
    for sibling in heading.next_siblings:
        name = getattr(sibling, "name", None)
        if name in {"h1", "h2", "h3", "h4"}:
            break
        get_text = getattr(sibling, "get_text", None)
        if callable(get_text):
            text = get_text(" ", strip=True)
            if text:
                chunks.append(text)
    return " ".join(chunks).strip()


def _extract_status_from_doc_page(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(
        lambda tag: tag.name in {"h1", "h2", "h3", "h4"}
        and "status" in tag.get_text(" ", strip=True).lower()
    )
    if not heading:
        text = soup.get_text("\n", strip=True)
        # Fallback for pages where WG state appears as plain text near top metadata.
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("WG ") or line.startswith("In WG ") or line.startswith(
                "Waiting for Implementation"
            ):
                return line
        return ""

    chunks: list[str] = []
    for sibling in heading.next_siblings:
        name = getattr(sibling, "name", None)
        if name in {"h1", "h2", "h3", "h4"}:
            break
        get_text = getattr(sibling, "get_text", None)
        if callable(get_text):
            text = get_text(" ", strip=True)
            if text:
                chunks.append(text)
    return " ".join(chunks).strip()


def _clean_status_text(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""

    # Drop non-status helper lines that often appear in status cells.
    drop_prefixes = (
        "I-D Exists",
        "Reviews:",
        "Review:",
        "Expires",
        "New",
    )
    filtered = [ln for ln in lines if not ln.startswith(drop_prefixes)]
    if not filtered:
        filtered = lines

    for line in filtered:
        if line.startswith("WG ") or line.startswith("In WG ") or line.startswith(
            "Waiting for Implementation"
        ):
            return re.sub(r"\s+", " ", line).strip()

    # Otherwise return the first meaningful line.
    return re.sub(r"\s+", " ", filtered[0]).strip()


def _extract_title_from_row_text(row_text: str, draft_name: str) -> str:
    compact = re.sub(r"\s+", " ", row_text).strip()
    # Example row: "... draft-ietf-bess-foo-03 Some Title 2025-10-17 I-D Exists ..."
    pattern = re.compile(
        rf"{re.escape(draft_name)}-\d+\s+(.*?)\s+\d{{4}}-\d{{2}}-\d{{2}}\b",
        flags=re.IGNORECASE,
    )
    match = pattern.search(compact)
    if match:
        return match.group(1).strip()
    return ""


def _extract_status_from_row_text(row_text: str) -> str:
    compact = re.sub(r"\s+", " ", row_text).strip()
    patterns = [
        r"WG Consensus:\s*Waiting for Write-Up Reviews?",
        r"WG Consensus:\s*Waiting for Write-Up",
        r"In WG Last Call\s*:\s*Proposed Standard",
        r"In WG Last Call\s*:\s*[A-Za-z ]+",
        r"WG Document\s*:\s*Proposed Standard Reviews?",
        r"WG Document\s*:\s*[A-Za-z ]+",
        r"WG Document",
    ]
    for pat in patterns:
        match = re.search(pat, compact, flags=re.IGNORECASE)
        if match:
            return re.sub(r"\s+", " ", match.group(0)).strip()
    return ""


def _fetch_draft_metadata_from_api(
    draft_name: str, timeout: int = 20
) -> tuple[str, str]:
    params = {"name": draft_name.lower()}
    try:
        response = requests.get(DOC_API_URL, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return "", ""

    objects = payload.get("objects", [])
    if not objects:
        return "", ""
    item = objects[0]
    title = str(item.get("title", "")).strip()
    abstract = str(item.get("abstract", "")).strip()
    return title, abstract


def _fetch_documents_page_drafts(
    acronym: str, timeout: int = 20, limit: int = 5
) -> list[tuple[str, str, str, str]]:
    """
    Return (draft_name, title, doc_url, status) from WG documents page.
    Page order is used as "top/latest" signal as requested.
    """
    url = WG_DOCUMENTS_URL_TEMPLATE.format(acronym=acronym.lower())
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DatatrackerError(f"Unable to fetch WG documents page: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    seen: set[str] = set()
    out: list[tuple[str, str, str, str]] = []

    # Primary parser: table rows with explicit status column.
    for row in soup.find_all("tr"):
        link = row.find("a", href=re.compile(r"/doc/draft-[a-z0-9-]+/?$"))
        if not link:
            continue

        href = str(link.get("href", "")).strip()
        m = re.search(r"/doc/(draft-[a-z0-9-]+)/?$", href.lower())
        if not m:
            continue
        draft = m.group(1)
        if draft in seen:
            continue
        seen.add(draft)

        tds = row.find_all("td")
        title = link.get_text(" ", strip=True)
        status = ""
        row_text = row.get_text(" ", strip=True)
        parsed_title = _extract_title_from_row_text(row_text, draft)
        parsed_status = _extract_status_from_row_text(row_text)
        if parsed_title:
            title = parsed_title
        if parsed_status:
            status = parsed_status

        if tds:
            doc_cell = tds[0]
            doc_lines = [x.strip() for x in doc_cell.get_text("\n", strip=True).splitlines()]
            for candidate in doc_lines:
                if candidate and not candidate.lower().startswith("draft-"):
                    if not title:
                        title = candidate
                    break
            if len(tds) >= 3:
                cell_status = _clean_status_text(tds[2].get_text("\n", strip=True))
                if cell_status:
                    status = cell_status

        doc_url = "https://datatracker.ietf.org" + href
        out.append((draft, title, doc_url, status))
        if len(out) >= limit:
            break

    # Fallback parser: if no table rows were parsed, use simple link scan.
    if not out:
        links = soup.find_all("a", href=re.compile(r"/doc/draft-[a-z0-9-]+/?$"))
        for link in links:
            href = str(link.get("href", "")).strip()
            m = re.search(r"/doc/(draft-[a-z0-9-]+)/?$", href.lower())
            if not m:
                continue
            draft = m.group(1)
            if draft in seen:
                continue
            seen.add(draft)
            title = link.get_text(" ", strip=True)
            doc_url = "https://datatracker.ietf.org" + href
            out.append((draft, title, doc_url, ""))
            if len(out) >= limit:
                break

    return out


def fetch_top_active_drafts(
    acronym: str, timeout: int = 20, limit: int = 5
) -> list[DraftInfo]:
    """Fetch top/latest drafts from WG documents page and include metadata.

    Section 3 entry point.
    Flow: list page parse -> row extraction -> detail/API enrichment.
    """
    draft_rows = _fetch_documents_page_drafts(acronym, timeout=timeout, limit=limit)
    results: list[DraftInfo] = []

    for draft_name, title, doc_url, status in draft_rows:
        abstract = ""
        page_status = ""
        try:
            response = requests.get(doc_url, timeout=timeout)
            response.raise_for_status()
            abstract = _extract_abstract_from_doc_page(response.text)
            page_status = _extract_status_from_doc_page(response.text)
        except requests.RequestException:
            abstract = ""
            page_status = ""

        api_title, api_abstract = _fetch_draft_metadata_from_api(draft_name, timeout=timeout)
        if api_title and (not title or title.lower().startswith("draft-")):
            title = api_title
        if not abstract and api_abstract:
            abstract = api_abstract
        if not abstract:
            abstract = "Abstract not found."
        if not status:
            status = page_status
        if not status:
            status = "Status not found."

        results.append(
            DraftInfo(
                name=draft_name,
                title=title.strip(),
                status=status.strip(),
                abstract=abstract.strip(),
                url=doc_url,
            )
        )
    return results


def _parse_mailarchive_date(value: str) -> Optional[datetime]:
    if not value:
        return None
    clean = value.strip().replace("Z", "+00:00")
    candidates = [
        clean,
        clean.split(" ")[0],
    ]
    for candidate in candidates:
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue
    return None


def _to_utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def _extract_discussion_posts_from_page(
    html: str, acronym: str
) -> list[tuple[Optional[datetime], DiscussionPost]]:
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=re.compile(rf"/arch/msg/{re.escape(acronym.lower())}/"))

    out: list[tuple[Optional[datetime], DiscussionPost]] = []
    seen: set[str] = set()
    for link in links:
        href = str(link.get("href", "")).strip()
        if not href:
            continue
        abs_url = "https://mailarchive.ietf.org" + href
        if abs_url in seen:
            continue
        seen.add(abs_url)

        subject = link.get_text(" ", strip=True) or "(no subject)"
        container = link.find_parent(["tr", "li", "article", "div"]) or link.parent

        date_obj: Optional[datetime] = None
        date_text = ""
        time_tag = container.find("time") if container else None
        if time_tag:
            date_text = str(time_tag.get("datetime", "")).strip() or time_tag.get_text(
                " ", strip=True
            )
            date_obj = _parse_mailarchive_date(date_text)

        author = ""
        if container:
            container_text = container.get_text("\n", strip=True)
            for line in container_text.splitlines():
                line = line.strip()
                if line.lower().startswith("from:"):
                    author = line.split(":", 1)[1].strip()
                    break
            if not author:
                m = re.search(r"\bby\s+([A-Za-z0-9 .,'_-]{3,})", container_text)
                if m:
                    author = m.group(1).strip()

        out.append(
            (
                date_obj,
                DiscussionPost(
                    date=date_text or "Unknown date",
                    subject=subject,
                    author=author or "Unknown author",
                    url=abs_url,
                ),
            )
        )
    return out


def fetch_wg_discussions_last_months(
    acronym: str, months: int = 3, timeout: int = 20, max_pages: int = 3
) -> list[DiscussionPost]:
    """Fetch WG discussion messages from mailarchive for the last N months.

    Section 4 entry point.
    Flow: browse page parse -> date filter -> bounded pagination.
    """
    url = MAILARCHIVE_BROWSE_URL_TEMPLATE.format(acronym=acronym.lower())
    cutoff = datetime.utcnow() - timedelta(days=max(1, months) * 30)

    collected: list[tuple[Optional[datetime], DiscussionPost]] = []
    visited: set[str] = set()

    for _ in range(max_pages):
        if url in visited:
            break
        visited.add(url)

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise DatatrackerError(f"Unable to fetch WG discussions: {exc}") from exc

        page_items = _extract_discussion_posts_from_page(response.text, acronym=acronym)
        if not page_items:
            break

        for dt, post in page_items:
            if dt is None or _to_utc_naive(dt) >= cutoff:
                collected.append((dt, post))

        soup = BeautifulSoup(response.text, "html.parser")
        older = soup.find(
            "a",
            string=lambda s: isinstance(s, str) and "older" in s.lower(),
        )
        if not older:
            older = soup.find("a", rel=lambda rel: rel and "next" in rel)
        if older and older.get("href"):
            href = str(older.get("href")).strip()
            if href.startswith("http"):
                url = href
            else:
                url = "https://mailarchive.ietf.org" + href
        else:
            break

    collected.sort(key=lambda item: item[0] or datetime.min, reverse=True)
    deduped: list[DiscussionPost] = []
    seen_urls: set[str] = set()
    for _, post in collected:
        if post.url in seen_urls:
            continue
        seen_urls.add(post.url)
        deduped.append(post)
    return deduped


def fetch_wg_discussions_last_day(
    acronym: str, days: int = 1, timeout: int = 20, max_pages: int = 2
) -> list[DiscussionPost]:
    """Fetch WG discussion messages from mailarchive for the last N days."""
    url = MAILARCHIVE_BROWSE_URL_TEMPLATE.format(acronym=acronym.lower())
    cutoff = datetime.utcnow() - timedelta(days=max(1, days))

    collected: list[tuple[Optional[datetime], DiscussionPost]] = []
    visited: set[str] = set()

    for _ in range(max_pages):
        if url in visited:
            break
        visited.add(url)

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise DatatrackerError(f"Unable to fetch WG discussions: {exc}") from exc

        page_items = _extract_discussion_posts_from_page(response.text, acronym=acronym)
        if not page_items:
            break

        for dt, post in page_items:
            # For daily updates we send only when date can be verified in the last day.
            if dt is not None and _to_utc_naive(dt) >= cutoff:
                collected.append((dt, post))

        soup = BeautifulSoup(response.text, "html.parser")
        older = soup.find(
            "a",
            string=lambda s: isinstance(s, str) and "older" in s.lower(),
        )
        if not older:
            older = soup.find("a", rel=lambda rel: rel and "next" in rel)
        if older and older.get("href"):
            href = str(older.get("href")).strip()
            if href.startswith("http"):
                url = href
            else:
                url = "https://mailarchive.ietf.org" + href
        else:
            break

    collected.sort(key=lambda item: item[0] or datetime.min, reverse=True)
    deduped: list[DiscussionPost] = []
    seen_urls: set[str] = set()
    for _, post in collected:
        if post.url in seen_urls:
            continue
        seen_urls.add(post.url)
        deduped.append(post)
    return deduped


def _absolute_url(base: str, href: str) -> str:
    href = href.strip()
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return base.rstrip("/") + href


def _extract_meeting_label(raw_text: str, fallback: str) -> str:
    text = re.sub(r"\s+", " ", raw_text).strip()
    m_num = re.search(r"\bIETF\s*([0-9]{2,3})\b", text, flags=re.IGNORECASE)
    if m_num:
        return f"IETF {m_num.group(1)}"

    m_name = re.search(
        r"\b(?:March|April|May|June|July|August|September|October|November|December|January|February)\s+\d{4}\b",
        text,
        flags=re.IGNORECASE,
    )
    if m_name:
        return m_name.group(0)
    return fallback


def fetch_updates_from_last_two_meetings(
    acronym: str, timeout: int = 20, limit: int = 2
) -> list[MeetingUpdate]:
    """Fetch agenda/minutes links for the most recent WG meetings."""
    url = WG_MEETINGS_URL_TEMPLATE.format(acronym=acronym.lower())
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DatatrackerError(f"Unable to fetch WG meetings page: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)

    by_meeting: dict[str, dict[str, list[str]]] = {}
    meeting_order: list[str] = []
    fallback_counter = 0

    for link in links:
        href = str(link.get("href", "")).strip()
        text = link.get_text(" ", strip=True).lower()
        href_l = href.lower()

        kind = ""
        if "agenda" in text or "agenda" in href_l:
            kind = "agendas"
        elif "minute" in text or "minutes" in href_l:
            kind = "minutes"
        else:
            continue

        container = link.find_parent(["tr", "li", "article", "section", "div"]) or link
        container_text = container.get_text(" ", strip=True)
        heading = container.find_previous(["h2", "h3", "h4"])
        heading_text = heading.get_text(" ", strip=True) if heading else ""

        fallback_counter += 1
        label = _extract_meeting_label(
            f"{heading_text} {container_text}", fallback=f"Meeting {fallback_counter}"
        )

        if label not in by_meeting:
            by_meeting[label] = {"agendas": [], "minutes": []}
            meeting_order.append(label)

        abs_url = _absolute_url("https://datatracker.ietf.org", href)
        if abs_url not in by_meeting[label][kind]:
            by_meeting[label][kind].append(abs_url)

    updates: list[MeetingUpdate] = []
    for label in meeting_order:
        payload = by_meeting[label]
        if not payload["agendas"] and not payload["minutes"]:
            continue
        updates.append(
            MeetingUpdate(
                meeting=label,
                agendas=payload["agendas"],
                minutes=payload["minutes"],
            )
        )
        if len(updates) >= limit:
            break
    return updates


def _extract_next_meeting_number(index_html: str) -> Optional[str]:
    soup = BeautifulSoup(index_html, "html.parser")
    nums: list[int] = []
    for link in soup.find_all("a", href=True):
        href = str(link.get("href", ""))
        m = re.search(r"/meeting/([0-9]{2,3})/?$", href)
        if m:
            nums.append(int(m.group(1)))
    if not nums:
        return None
    return str(max(nums))


def _extract_meeting_numbers(index_html: str) -> list[str]:
    soup = BeautifulSoup(index_html, "html.parser")
    nums: set[int] = set()
    for link in soup.find_all("a", href=True):
        href = str(link.get("href", ""))
        m = re.search(r"/meeting/([0-9]{2,3})/?$", href)
        if m:
            nums.add(int(m.group(1)))
    return [str(n) for n in sorted(nums, reverse=True)]


def _extract_meeting_dates_and_place(meeting_html: str) -> tuple[str, str]:
    text = BeautifulSoup(meeting_html, "html.parser").get_text(" ", strip=True)
    dates_match = re.search(
        r"([A-Z][a-z]+ \d{1,2}, \d{4}\s*-\s*[A-Z][a-z]+ \d{1,2}, \d{4})",
        text,
    )
    dates = dates_match.group(1) if dates_match else "Dates TBD"

    place_match = re.search(
        r"(?:Location|Venue)\s*[:\-]\s*([A-Za-z0-9, .()/-]{3,120})", text
    )
    place = place_match.group(1).strip() if place_match else "Place TBD"
    return dates, place


def _extract_meeting_end_date(meeting_html: str) -> Optional[date_cls]:
    text = BeautifulSoup(meeting_html, "html.parser").get_text(" ", strip=True)
    m = re.search(
        r"([A-Z][a-z]+ \d{1,2}, \d{4})\s*-\s*([A-Z][a-z]+ \d{1,2}, \d{4})",
        text,
    )
    if not m:
        return None
    try:
        return datetime.strptime(m.group(2), "%B %d, %Y").date()
    except ValueError:
        return None


def _extract_agenda_links_for_meeting(meetings_html: str, meeting_number: str) -> list[str]:
    soup = BeautifulSoup(meetings_html, "html.parser")
    links: list[str] = []
    seen: set[str] = set()

    for link in soup.find_all("a", href=True):
        href = str(link.get("href", "")).strip()
        txt = link.get_text(" ", strip=True).lower()
        if "agenda" not in txt and "agenda" not in href.lower():
            continue

        container = link.find_parent(["tr", "li", "article", "div", "section"]) or link
        container_text = container.get_text(" ", strip=True)
        heading = container.find_previous(["h1", "h2", "h3", "h4"])
        heading_text = heading.get_text(" ", strip=True) if heading else ""
        context = f"{heading_text} {container_text}"
        if meeting_number not in context and f"IETF {meeting_number}" not in context:
            # Keep only links clearly associated with the target meeting.
            continue

        abs_url = _absolute_url("https://datatracker.ietf.org", href)
        if abs_url not in seen:
            seen.add(abs_url)
            links.append(abs_url)

    return links


def _extract_agenda_body(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(
        lambda tag: tag.name in {"h1", "h2", "h3", "h4"}
        and "agenda" in tag.get_text(" ", strip=True).lower()
    )
    if heading:
        chunks: list[str] = []
        for sibling in heading.next_siblings:
            name = getattr(sibling, "name", None)
            if name in {"h1", "h2", "h3", "h4"}:
                break
            get_text = getattr(sibling, "get_text", None)
            if callable(get_text):
                text = get_text(" ", strip=True)
                if text:
                    chunks.append(text)
        body = " ".join(chunks).strip()
        if body:
            return body

    text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _extract_minutes_body(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(
        lambda tag: tag.name in {"h1", "h2", "h3", "h4"}
        and "minute" in tag.get_text(" ", strip=True).lower()
    )
    if heading:
        chunks: list[str] = []
        for sibling in heading.next_siblings:
            name = getattr(sibling, "name", None)
            if name in {"h1", "h2", "h3", "h4"}:
                break
            get_text = getattr(sibling, "get_text", None)
            if callable(get_text):
                text = get_text(" ", strip=True)
                if text:
                    chunks.append(text)
        body = " ".join(chunks).strip()
        if body:
            return body
    text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _summarize_agenda_text(text: str) -> str:
    if not text:
        return "Agenda summary unavailable."
    # Lightweight deterministic summary for agenda body.
    compact = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", compact)
    selected = [s.strip() for s in sentences if len(s.strip()) > 30][:2]
    if selected:
        return " ".join(selected)
    return compact[:280] + ("..." if len(compact) > 280 else "")


def _extract_meeting_links_for_number(
    meetings_html: str, meeting_number: str
) -> tuple[list[str], list[str]]:
    soup = BeautifulSoup(meetings_html, "html.parser")
    agendas: list[str] = []
    minutes: list[str] = []
    seen_ag: set[str] = set()
    seen_min: set[str] = set()

    for link in soup.find_all("a", href=True):
        href = str(link.get("href", "")).strip()
        text = link.get_text(" ", strip=True).lower()
        href_l = href.lower()

        kind = ""
        if "agenda" in text or "agenda" in href_l:
            kind = "agenda"
        elif "minute" in text or "minutes" in href_l:
            kind = "minutes"
        else:
            continue

        container = link.find_parent(["tr", "li", "article", "div", "section"]) or link
        container_text = container.get_text(" ", strip=True)
        heading = container.find_previous(["h1", "h2", "h3", "h4"])
        heading_text = heading.get_text(" ", strip=True) if heading else ""
        context = f"{heading_text} {container_text}"
        if meeting_number not in context and f"IETF {meeting_number}" not in context:
            continue

        abs_url = _absolute_url("https://datatracker.ietf.org", href)
        if kind == "agenda":
            if abs_url not in seen_ag:
                seen_ag.add(abs_url)
                agendas.append(abs_url)
        else:
            if abs_url not in seen_min:
                seen_min.add(abs_url)
                minutes.append(abs_url)
    return agendas, minutes


def fetch_upcoming_ietf_agenda(
    groups: Iterable[WorkingGroup], timeout: int = 20
) -> tuple[str, list[UpcomingAgendaItem]]:
    """
    Fetch next IETF meeting metadata and summarize available WG agendas.

    For each WG, agenda is included only if present (typically published shortly
    before the meeting).
    """
    try:
        idx_resp = requests.get(MEETINGS_INDEX_URL, timeout=timeout)
        idx_resp.raise_for_status()
    except requests.RequestException as exc:
        raise DatatrackerError(f"Unable to fetch IETF meetings index: {exc}") from exc

    meeting_number = _extract_next_meeting_number(idx_resp.text)
    if not meeting_number:
        raise DatatrackerError("Unable to determine next IETF meeting number")

    meeting_page = MEETING_PAGE_URL_TEMPLATE.format(number=meeting_number)
    try:
        mtg_resp = requests.get(meeting_page, timeout=timeout)
        mtg_resp.raise_for_status()
    except requests.RequestException as exc:
        raise DatatrackerError(f"Unable to fetch meeting page: {exc}") from exc

    dates, place = _extract_meeting_dates_and_place(mtg_resp.text)
    header = f"IETF {meeting_number} - {dates} - {place}"

    items: list[UpcomingAgendaItem] = []
    for wg in groups:
        url = WG_MEETINGS_URL_TEMPLATE.format(acronym=wg.acronym.lower())
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
        except requests.RequestException:
            continue

        agenda_links = _extract_agenda_links_for_meeting(resp.text, meeting_number)
        if not agenda_links:
            continue

        agenda_url = agenda_links[0]
        try:
            agenda_resp = requests.get(agenda_url, timeout=timeout)
            agenda_resp.raise_for_status()
            agenda_text = _extract_agenda_body(agenda_resp.text)
        except requests.RequestException:
            agenda_text = ""

        items.append(
            UpcomingAgendaItem(
                wg_acronym=wg.acronym,
                wg_name=wg.name,
                agenda_url=agenda_url,
                agenda_summary=_summarize_agenda_text(agenda_text),
            )
        )

    return header, items


def _find_last_completed_meeting(timeout: int = 20) -> tuple[str, str]:
    try:
        idx_resp = requests.get(MEETINGS_INDEX_URL, timeout=timeout)
        idx_resp.raise_for_status()
    except requests.RequestException as exc:
        raise DatatrackerError(f"Unable to fetch IETF meetings index: {exc}") from exc

    numbers = _extract_meeting_numbers(idx_resp.text)
    if not numbers:
        raise DatatrackerError("Unable to determine IETF meeting list")

    today = date_cls.today()
    for number in numbers:
        page_url = MEETING_PAGE_URL_TEMPLATE.format(number=number)
        try:
            page_resp = requests.get(page_url, timeout=timeout)
            page_resp.raise_for_status()
        except requests.RequestException:
            continue
        end_date = _extract_meeting_end_date(page_resp.text)
        if end_date is None or end_date <= today:
            return number, page_resp.text

    raise DatatrackerError("Unable to determine last completed IETF meeting")


def fetch_summary_of_last_ietf_meeting(
    groups: Iterable[WorkingGroup], timeout: int = 20
) -> tuple[str, list[LastMeetingItem]]:
    """Find last completed IETF meeting and summarize WG meeting minutes."""
    meeting_number, meeting_html = _find_last_completed_meeting(timeout=timeout)
    dates, place = _extract_meeting_dates_and_place(meeting_html)
    header = f"IETF {meeting_number} - {dates} - {place}"

    items: list[LastMeetingItem] = []
    for wg in groups:
        meetings_url = WG_MEETINGS_URL_TEMPLATE.format(acronym=wg.acronym.lower())
        try:
            resp = requests.get(meetings_url, timeout=timeout)
            resp.raise_for_status()
        except requests.RequestException:
            continue

        agendas, minutes = _extract_meeting_links_for_number(resp.text, meeting_number)
        if not minutes:
            # WG did not meet or no minutes published for this meeting.
            continue

        agenda_url = agendas[0] if agendas else ""
        minutes_url = minutes[0]
        try:
            min_resp = requests.get(minutes_url, timeout=timeout)
            min_resp.raise_for_status()
            minutes_text = _extract_minutes_body(min_resp.text)
        except requests.RequestException:
            minutes_text = ""

        items.append(
            LastMeetingItem(
                wg_acronym=wg.acronym,
                wg_name=wg.name,
                agenda_url=agenda_url,
                minutes_url=minutes_url,
                minutes_summary=_summarize_agenda_text(minutes_text),
            )
        )
    return header, items
