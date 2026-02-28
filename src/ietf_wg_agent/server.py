from __future__ import annotations

"""MCP server surface for the agent.

Control flow:
1) Resolve WG query for each tool call.
2) Return suggestions if unresolved.
3) Delegate to core data/summarization modules.
"""

from ietf_wg_agent.daily import (
    deliver_daily_discussion_updates_emails,
    deliver_daily_emails,
    run_daily,
    run_daily_discussion_updates,
)
from ietf_wg_agent.ietf import (
    DatatrackerError,
    DiscussionPost,
    DraftInfo,
    LastMeetingItem,
    MeetingUpdate,
    UpcomingAgendaItem,
    fetch_charter_text,
    fetch_summary_of_last_ietf_meeting,
    fetch_top_active_drafts,
    fetch_updates_from_last_two_meetings,
    fetch_upcoming_ietf_agenda,
    fetch_wg_discussions_last_day,
    fetch_wg_discussions_last_months,
    fetch_working_groups,
    resolve_working_group,
    suggest_working_groups,
)
from ietf_wg_agent.summarizer import summarize_charter, summarize_discussions
from ietf_wg_agent.subscriptions import register_daily_update

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - depends on optional dependency
    FastMCP = None


if FastMCP is not None:
    mcp = FastMCP("ietf-wg-agent")

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
            lines.append(
                "No WG agendas are currently published for the upcoming IETF meeting."
            )
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

    @mcp.tool()
    def find_working_group(query: str) -> str:
        """Resolve acronym/full WG name (e.g. LSR -> Link State Routing)."""
        groups = fetch_working_groups()
        wg = resolve_working_group(query, groups)
        if not wg:
            suggestions = suggest_working_groups(query, groups, limit=5)
            if not suggestions:
                return f"No WG found for '{query}'."
            lines = [f"No exact WG found for '{query}'. Did you mean:"]
            for candidate in suggestions:
                lines.append(f"- {candidate.acronym.upper()} - {candidate.name}")
            return "\n".join(lines)
        return f"Matched: {wg.acronym.upper()} - {wg.name}"

    @mcp.tool()
    def summary_of_wg(query: str) -> str:
        """Fetch and summarize the charter for the selected working group."""
        try:
            groups = fetch_working_groups()
            wg = resolve_working_group(query, groups)
            if not wg:
                suggestions = suggest_working_groups(query, groups, limit=5)
                if not suggestions:
                    return f"No WG found for '{query}'."
                lines = [f"No exact WG found for '{query}'. Did you mean:"]
                for candidate in suggestions:
                    lines.append(f"- {candidate.acronym.upper()} - {candidate.name}")
                return "\n".join(lines)

            charter = fetch_charter_text(wg.acronym)
            summary = summarize_charter(charter)
            return f"WG: {wg.acronym.upper()} - {wg.name}\n{summary}"
        except DatatrackerError as exc:
            return f"Error: {exc}"

    @mcp.tool()
    def register_wg_daily_update(user_id: str, query: str) -> str:
        """Register a user for daily summary updates for a working group."""
        groups = fetch_working_groups()
        wg = resolve_working_group(query, groups)
        if not wg:
            suggestions = suggest_working_groups(query, groups, limit=5)
            if not suggestions:
                return f"No WG found for '{query}'."
            lines = [f"No exact WG found for '{query}'. Did you mean:"]
            for candidate in suggestions:
                lines.append(f"- {candidate.acronym.upper()} - {candidate.name}")
            return "\n".join(lines)

        register_daily_update(user_id=user_id, acronym=wg.acronym)
        return f"Registered {user_id} for {wg.acronym.upper()} daily updates."

    @mcp.tool()
    def active_drafts_and_recent_rfcs(query: str) -> str:
        """Fetch top 5 active drafts and abstracts from WG documents page."""
        groups = fetch_working_groups()
        wg = resolve_working_group(query, groups)
        if not wg:
            suggestions = suggest_working_groups(query, groups, limit=5)
            if not suggestions:
                return f"No WG found for '{query}'."
            lines = [f"No exact WG found for '{query}'. Did you mean:"]
            for candidate in suggestions:
                lines.append(f"- {candidate.acronym.upper()} - {candidate.name}")
            return "\n".join(lines)

        drafts = fetch_top_active_drafts(wg.acronym, limit=5)
        body = _format_active_drafts(drafts)
        return f"WG: {wg.acronym.upper()} - {wg.name}\n{body}"

    @mcp.tool()
    def active_drafts(query: str) -> str:
        """Fetch top 5 active drafts and abstracts from WG documents page."""
        return active_drafts_and_recent_rfcs(query)

    @mcp.tool()
    def draft_discussions_summary(query: str) -> str:
        """Fetch WG draft discussions and summarize the last 3 months."""
        groups = fetch_working_groups()
        wg = resolve_working_group(query, groups)
        if not wg:
            suggestions = suggest_working_groups(query, groups, limit=5)
            if not suggestions:
                return f"No WG found for '{query}'."
            lines = [f"No exact WG found for '{query}'. Did you mean:"]
            for candidate in suggestions:
                lines.append(f"- {candidate.acronym.upper()} - {candidate.name}")
            return "\n".join(lines)

        posts = fetch_wg_discussions_last_months(wg.acronym, months=3)
        return f"WG: {wg.acronym.upper()} - {wg.name}\n{_format_discussions(posts)}"

    @mcp.tool()
    def daily_updates_summary(query: str) -> str:
        """Summarize WG discussions from the last 1 day."""
        groups = fetch_working_groups()
        wg = resolve_working_group(query, groups)
        if not wg:
            suggestions = suggest_working_groups(query, groups, limit=5)
            if not suggestions:
                return f"No WG found for '{query}'."
            lines = [f"No exact WG found for '{query}'. Did you mean:"]
            for candidate in suggestions:
                lines.append(f"- {candidate.acronym.upper()} - {candidate.name}")
            return "\n".join(lines)

        posts = fetch_wg_discussions_last_day(wg.acronym, days=1)
        body = summarize_discussions(posts, max_subjects=8, period_label="last 1 day")
        return f"WG: {wg.acronym.upper()} - {wg.name}\n{body}"

    @mcp.tool()
    def updates_from_last_2_ietf_meetings(query: str) -> str:
        """Fetch agendas and minutes for the last 2 WG meetings."""
        groups = fetch_working_groups()
        wg = resolve_working_group(query, groups)
        if not wg:
            suggestions = suggest_working_groups(query, groups, limit=5)
            if not suggestions:
                return f"No WG found for '{query}'."
            lines = [f"No exact WG found for '{query}'. Did you mean:"]
            for candidate in suggestions:
                lines.append(f"- {candidate.acronym.upper()} - {candidate.name}")
            return "\n".join(lines)

        updates = fetch_updates_from_last_two_meetings(wg.acronym, limit=2)
        return f"WG: {wg.acronym.upper()} - {wg.name}\n{_format_meeting_updates(updates)}"

    @mcp.tool()
    def run_daily_updates_summary_now() -> str:
        """Generate daily discussion-update summaries immediately."""
        return run_daily_discussion_updates(days=1)

    @mcp.tool()
    def send_daily_updates_now() -> str:
        """Send daily discussion-update emails if any updates exist."""
        try:
            return deliver_daily_discussion_updates_emails(days=1)
        except ValueError as exc:
            return f"Email not configured: {exc}"

    @mcp.tool()
    def agenda_of_upcoming_ietf_meeting() -> str:
        """Find next IETF meeting and summarize available WG agendas."""
        groups = fetch_working_groups()
        header, items = fetch_upcoming_ietf_agenda(groups)
        return _format_upcoming_ietf_agenda(header, items)

    @mcp.tool()
    def summary_of_last_ietf_meeting() -> str:
        """Summarize WG minutes from the last completed IETF meeting."""
        groups = fetch_working_groups()
        header, items = fetch_summary_of_last_ietf_meeting(groups)
        return _format_last_ietf_meeting_summary(header, items)

    @mcp.tool()
    def run_daily_summary_now() -> str:
        """Generate daily summaries immediately from current subscriptions."""
        return run_daily()

    @mcp.tool()
    def send_daily_emails_now() -> str:
        """Send daily summary emails immediately from current subscriptions."""
        try:
            return deliver_daily_emails()
        except ValueError as exc:
            return f"Email not configured: {exc}"


def main() -> None:
    if FastMCP is None:
        raise RuntimeError(
            "MCP support is optional and not installed. Run: pip install -e '.[mcp]'"
        )

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
