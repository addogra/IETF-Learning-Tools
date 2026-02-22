# Author: Aditya Dogra
from __future__ import annotations

"""Daily orchestration pipeline.

Control flow:
1) Build report content per subscribed user.
2) Attempt email delivery for each user report.
3) Persist execution report to disk.
"""

from datetime import date
from pathlib import Path

from ietf_wg_agent.ietf import (
    DiscussionPost,
    DatatrackerError,
    LastMeetingItem,
    MeetingUpdate,
    UpcomingAgendaItem,
    fetch_charter_text,
    fetch_summary_of_last_ietf_meeting,
    fetch_upcoming_ietf_agenda,
    fetch_working_groups,
    fetch_wg_discussions_last_day,
    fetch_updates_from_last_two_meetings,
)
from ietf_wg_agent.notifier import SMTPConfig, load_smtp_config, send_email
from ietf_wg_agent.summarizer import summarize_charter, summarize_discussions
from ietf_wg_agent.subscriptions import list_subscriptions


def _format_meeting_updates(updates: list[MeetingUpdate]) -> str:
    lines = ["Updates from last 2 IETF meetings:"]
    if not updates:
        lines.append("- No meeting updates found.")
        return "\n".join(lines)

    for update in updates:
        lines.append(f"- {update.meeting}")
        if update.agendas:
            lines.append("  Agendas:")
            for url in update.agendas:
                lines.append(f"  - {url}")
        else:
            lines.append("  Agendas: Not found")
        if update.minutes:
            lines.append("  Minutes:")
            for url in update.minutes:
                lines.append(f"  - {url}")
        else:
            lines.append("  Minutes: Not found")
        lines.append("")
    return "\n".join(lines)


def _format_upcoming_ietf_agenda(header: str, items: list[UpcomingAgendaItem]) -> str:
    lines = [header, ""]
    if not items:
        lines.append("No WG agendas are currently published for the upcoming IETF meeting.")
        return "\n".join(lines)

    for item in items:
        lines.append(f"Working Group {item.wg_name} ({item.wg_acronym.upper()})")
        lines.append(f"- Agenda: {item.agenda_url}")
        lines.append(f"- Summary: {item.agenda_summary}")
        lines.append("")
    return "\n".join(lines).strip()


def _format_last_ietf_meeting_summary(header: str, items: list[LastMeetingItem]) -> str:
    lines = [header, ""]
    if not items:
        lines.append(
            "No working groups with published minutes were found for the last IETF meeting."
        )
        return "\n".join(lines)

    for item in items:
        lines.append(f"Working Group {item.wg_name} ({item.wg_acronym.upper()})")
        if item.agenda_url:
            lines.append(f"- Agenda: {item.agenda_url}")
        lines.append(f"- Minutes: {item.minutes_url}")
        lines.append(f"- Summary: {item.minutes_summary}")
        lines.append("")
    return "\n".join(lines).strip()


def _format_daily_discussion_updates(posts: list[DiscussionPost]) -> str:
    return summarize_discussions(
        posts, months=3, max_subjects=8, period_label="last 1 day"
    )


def _build_user_reports() -> dict[str, str]:
    # Section 1: Build one summary body per user from subscriptions.
    today = date.today().isoformat()
    subs = list_subscriptions()
    if not subs:
        return {}

    by_user: dict[str, list[str]] = {}
    for sub in subs:
        by_user.setdefault(sub.user_id, []).append(sub.acronym)

    # Fetch upcoming meeting agenda once, then filter per user's subscribed WGs.
    upcoming_header = ""
    upcoming_items: list[UpcomingAgendaItem] = []
    last_header = ""
    last_items: list[LastMeetingItem] = []
    try:
        groups = fetch_working_groups()
        upcoming_header, upcoming_items = fetch_upcoming_ietf_agenda(groups)
        last_header, last_items = fetch_summary_of_last_ietf_meeting(groups)
    except DatatrackerError:
        upcoming_header, upcoming_items = "", []
        last_header, last_items = "", []

    reports: dict[str, str] = {}
    for user_id, acronyms in by_user.items():
        lines = [f"IETF WG Daily Summary - {today}", f"Recipient: {user_id}", ""]
        for acronym in sorted(set(acronyms)):
            lines.append(f"WG: {acronym.upper()}")
            try:
                charter = fetch_charter_text(acronym)
                lines.append(summarize_charter(charter))
            except DatatrackerError as exc:
                lines.append(f"Error: {exc}")
            try:
                updates = fetch_updates_from_last_two_meetings(acronym, limit=2)
                lines.append(_format_meeting_updates(updates))
            except DatatrackerError as exc:
                lines.append(f"Meeting update error: {exc}")
            lines.append("")

        if upcoming_header:
            filtered = [
                item
                for item in upcoming_items
                if item.wg_acronym.lower() in {a.lower() for a in acronyms}
            ]
            lines.append(_format_upcoming_ietf_agenda(upcoming_header, filtered))
            lines.append("")

        if last_header:
            filtered_last = [
                item
                for item in last_items
                if item.wg_acronym.lower() in {a.lower() for a in acronyms}
            ]
            lines.append(_format_last_ietf_meeting_summary(last_header, filtered_last))
            lines.append("")
        reports[user_id] = "\n".join(lines).strip()
    return reports


def run_daily() -> str:
    # Section 2: Produce printable combined report for terminal/logging.
    reports = _build_user_reports()
    if not reports:
        return "No subscriptions found."

    lines: list[str] = []
    for user_id in sorted(reports):
        lines.append(f"===== {user_id} =====")
        lines.append(reports[user_id])
        lines.append("")
    return "\n".join(lines).strip()


def _build_user_discussion_reports(days: int = 1) -> dict[str, str]:
    today = date.today().isoformat()
    subs = list_subscriptions()
    if not subs:
        return {}

    by_user: dict[str, list[str]] = {}
    for sub in subs:
        by_user.setdefault(sub.user_id, []).append(sub.acronym)

    reports: dict[str, str] = {}
    for user_id, acronyms in by_user.items():
        lines = [f"IETF WG Daily Discussion Updates - {today}", f"Recipient: {user_id}", ""]
        has_updates = False
        for acronym in sorted(set(acronyms)):
            lines.append(f"WG: {acronym.upper()}")
            try:
                posts = fetch_wg_discussions_last_day(acronym, days=days)
                if posts:
                    has_updates = True
                    lines.append(_format_daily_discussion_updates(posts))
                else:
                    lines.append("No discussion posts in the last 1 day.")
            except DatatrackerError as exc:
                lines.append(f"Discussion update error: {exc}")
            lines.append("")

        if has_updates:
            reports[user_id] = "\n".join(lines).strip()
    return reports


def run_daily_discussion_updates(days: int = 1) -> str:
    reports = _build_user_discussion_reports(days=days)
    if not reports:
        return "No discussion updates found in the last 1 day."

    lines: list[str] = []
    for user_id in sorted(reports):
        lines.append(f"===== {user_id} =====")
        lines.append(reports[user_id])
        lines.append("")
    return "\n".join(lines).strip()


def deliver_daily_emails() -> str:
    # Section 3: Deliver per-user report via SMTP and collect outcomes.
    reports = _build_user_reports()
    if not reports:
        return "No subscriptions found. No emails sent."

    config = load_smtp_config()
    today = date.today().isoformat()
    delivered = 0
    skipped: list[str] = []

    for user_id, body in reports.items():
        if "@" not in user_id:
            skipped.append(user_id)
            continue
        try:
            send_email(
                to_email=user_id,
                subject=f"IETF WG Daily Summary - {today}",
                body=body,
                config=config,
            )
            delivered += 1
        except Exception as exc:
            skipped.append(f"{user_id} (send failed: {exc})")

    status = [
        f"Emails delivered: {delivered}",
        (
            f"Delivery settings: retries={config.retries}, "
            f"backoff_seconds={config.backoff_seconds}, "
            f"jitter_seconds={config.jitter_seconds}"
        ),
    ]
    if skipped:
        status.append("Skipped:")
        for item in skipped:
            status.append(f"- {item}")
    return "\n".join(status)


def deliver_daily_discussion_updates_emails(days: int = 1) -> str:
    reports = _build_user_discussion_reports(days=days)
    if not reports:
        return "No discussion updates in the last 1 day. No emails sent."

    config: SMTPConfig = load_smtp_config()
    today = date.today().isoformat()
    delivered = 0
    skipped: list[str] = []

    for user_id, body in reports.items():
        if "@" not in user_id:
            skipped.append(user_id)
            continue
        try:
            send_email(
                to_email=user_id,
                subject=f"IETF WG Daily Discussion Updates - {today}",
                body=body,
                config=config,
            )
            delivered += 1
        except Exception as exc:
            skipped.append(f"{user_id} (send failed: {exc})")

    status = [
        f"Discussion update emails delivered: {delivered}",
        (
            f"Delivery settings: retries={config.retries}, "
            f"backoff_seconds={config.backoff_seconds}, "
            f"jitter_seconds={config.jitter_seconds}"
        ),
    ]
    if skipped:
        status.append("Skipped:")
        for item in skipped:
            status.append(f"- {item}")
    return "\n".join(status)


def main() -> None:
    # Section 4: Execute full daily job and persist artifact.
    report = run_daily()
    email_status = ""
    try:
        email_status = deliver_daily_emails()
    except ValueError as exc:
        email_status = f"Email not configured: {exc}"

    discussion_status = ""
    try:
        discussion_status = deliver_daily_discussion_updates_emails(days=1)
    except ValueError as exc:
        discussion_status = f"Discussion email not configured: {exc}"

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / f"daily-{date.today().isoformat()}.txt"
    lines = [report, "", email_status, "", discussion_status]
    filename.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(report)
    print("")
    print(email_status)
    print("")
    print(discussion_status)
    print(f"\nSaved: {filename}")


if __name__ == "__main__":
    main()
