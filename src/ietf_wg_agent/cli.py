# Author: Aditya Dogra
from __future__ import annotations

"""Interactive CLI orchestration.

Control flow:
1) Collect and validate user inputs.
2) Resolve WG (or run suggestion disambiguation).
3) Optional subscription registration.
4) Execute selected option and render formatted output.
"""

import shutil
import subprocess
import sys

from ietf_wg_agent.ietf import (
    DatatrackerError,
    DiscussionPost,
    DraftInfo,
    MeetingUpdate,
    LastMeetingItem,
    UpcomingAgendaItem,
    fetch_charter_text,
    fetch_summary_of_last_ietf_meeting,
    fetch_upcoming_ietf_agenda,
    fetch_top_active_drafts,
    fetch_updates_from_last_two_meetings,
    fetch_wg_discussions_last_day,
    fetch_wg_discussions_last_months,
    fetch_working_groups,
    resolve_working_group,
    suggest_working_groups,
)
from ietf_wg_agent.summarizer import summarize_charter, summarize_discussions
from ietf_wg_agent.subscriptions import register_daily_update


def _format_active_drafts(drafts: list[DraftInfo]) -> str:
    lines = ["Top 5 active drafts from WG documents:"]
    if not drafts:
        lines.append("- No drafts found.")
        return "\n".join(lines)

    for draft in drafts:
        lines.append(f"- {draft.name}")
        if draft.title:
            lines.append(f"  Title: {draft.title}")
        lines.append(f"  Status: {draft.status}")
        lines.append(f"  URL: {draft.url}")
        lines.append(f"  Abstract: {draft.abstract}")
        lines.append("")
    return "\n".join(lines)


def _format_discussions(posts: list[DiscussionPost]) -> str:
    return summarize_discussions(posts, months=3, max_subjects=5)


def _format_daily_updates(posts: list[DiscussionPost]) -> str:
    return summarize_discussions(posts, max_subjects=8, period_label="last 1 day")


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


def _start_daily_updates_scheduler() -> str:
    cmd = shutil.which("ietf-wg-daily-updates-scheduler")
    if not cmd:
        return (
            "Scheduler command not found. Run manually after install: "
            "ietf-wg-daily-updates-scheduler"
        )

    kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform != "win32":
        kwargs["start_new_session"] = True

    try:
        proc = subprocess.Popen([cmd], **kwargs)
        return f"Daily updates scheduler started (pid={proc.pid})."
    except Exception as exc:
        return (
            "Unable to auto-start scheduler. Run manually: "
            f"ietf-wg-daily-updates-scheduler (error: {exc})"
        )


def main() -> None:
    # Section 1: Input collection and validation.
    print("IETF WG Agent")
    print("------------")

    user_email = input("Email for daily updates: ").strip()
    if user_email and "@" not in user_email:
        print("Invalid email. Please enter a valid email address.")
        return

    wg_input = input("Working Group Name (full name or short form, e.g. LSR): ").strip()

    if not wg_input:
        print("No working group value supplied.")
        return

    try:
        # Section 2: WG resolution and typo-suggestion disambiguation.
        groups = fetch_working_groups()
        wg = resolve_working_group(wg_input, groups)
        if not wg:
            suggestions = suggest_working_groups(wg_input, groups, limit=5)
            if not suggestions:
                print(f"No WG found for input: {wg_input}")
                return

            print(f"No exact WG found for '{wg_input}'. Did you mean:")
            for idx, candidate in enumerate(suggestions, start=1):
                print(f"{idx}. {candidate.acronym.upper()} - {candidate.name}")

            choice = input(
                f"Select 1-{len(suggestions)} to continue, or press Enter to cancel: "
            ).strip()
            if not choice:
                print("Cancelled.")
                return
            if not choice.isdigit():
                print("Invalid choice.")
                return

            selection = int(choice)
            if selection < 1 or selection > len(suggestions):
                print("Invalid choice.")
                return
            wg = suggestions[selection - 1]
            print(f"Selected WG: {wg.acronym.upper()} - {wg.name}")

        print(f"Matched WG: {wg.acronym.upper()} - {wg.name}")

        # Section 3: Feature dispatch.
        print("\nOptions:")
        print("1. Summary of WG")
        print("2. Active drafts")
        print("3. Draft discussions in a WG (last 3 months)")
        print("4. Updates from last 2 IETF meetings")
        print("5. Daily updates (last 1 day + scheduler)")
        print("6. Agenda of upcoming IETF meeting")
        print("7. Summary of last IETF meeting")
        option = input("Select option: ").strip()

        # Section 4: Optional subscription persistence (skip for WG summary and active drafts).
        if user_email and option in {"3", "4", "5", "6", "7"}:
            enroll = input("Register this WG for daily updates? [y/N]: ").strip().lower()
            if enroll == "y":
                register_daily_update(user_id=user_email, acronym=wg.acronym)
                print("Daily update registration saved.")

        if option == "1":
            charter = fetch_charter_text(wg.acronym)
            print("\n" + summarize_charter(charter))
        elif option == "2":
            drafts = fetch_top_active_drafts(wg.acronym, limit=5)
            print("\n" + _format_active_drafts(drafts))
        elif option == "3":
            posts = fetch_wg_discussions_last_months(wg.acronym, months=3)
            print("\n" + _format_discussions(posts))
        elif option == "4":
            updates = fetch_updates_from_last_two_meetings(wg.acronym, limit=2)
            print("\n" + _format_meeting_updates(updates))
        elif option == "5":
            posts = fetch_wg_discussions_last_day(wg.acronym, days=1)
            print("\n" + _format_daily_updates(posts))
            start_sched = input("Start daily updates scheduler now? [y/N]: ").strip().lower()
            if start_sched == "y":
                print(_start_daily_updates_scheduler())
        elif option == "6":
            header, items = fetch_upcoming_ietf_agenda(groups)
            print("\n" + _format_upcoming_ietf_agenda(header, items))
        elif option == "7":
            header, items = fetch_summary_of_last_ietf_meeting(groups)
            print("\n" + _format_last_ietf_meeting_summary(header, items))
        else:
            print("Unsupported option.")

    except DatatrackerError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
