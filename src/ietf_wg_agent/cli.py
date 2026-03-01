from __future__ import annotations

"""Interactive CLI orchestration.

REQ-FEAT-001..006 flow in this module:
1) Select user type (new engineer vs experienced engineer).
2) Resolve WG by technology query or WG name.
3) Run iterative WG feature menu with Back/Quit navigation.
"""

from ietf_wg_agent.ietf import (
    DatatrackerError,
    DiscussionSummary,
    DraftResult,
    MeetingUpdates,
    WgMatch,
    WgResolutionResult,
    WorkingGroup,
    get_wg_active_drafts,
    get_wg_charter,
    get_wg_discussion_summary,
    get_wg_last_two_meeting_updates,
    resolve_wg_name,
    suggest_wgs_by_technology,
)


NAV_BACK = "__back__"
NAV_QUIT = "__quit__"
ACTIVE_DRAFTS_LIMIT = 10


def _read_nav_input(prompt: str) -> str:
    value = input(prompt).strip()
    low = value.lower()
    if low in {"b", "back"}:
        return NAV_BACK
    if low in {"q", "quit"}:
        return NAV_QUIT
    return value


def _format_technology_matches(query: str, matches: list[WgMatch]) -> str:
    lines = [f"Technology onboarding results for '{query}':"]
    if not matches:
        lines.append("- No WG matches found. Rebuild vector DB or broaden the query.")
        return "\n".join(lines)

    for idx, match in enumerate(matches, start=1):
        lines.append(
            f"{idx}. {match.acronym.upper()} - {match.name} "
            f"(score={match.score:.4f})"
        )
        lines.append(f"   {match.justification}")
    return "\n".join(lines)


def _format_active_drafts(drafts: list[DraftResult]) -> str:
    lines = ["Active drafts:"]
    if not drafts:
        lines.append("- No active drafts found.")
        return "\n".join(lines)

    for draft in drafts:
        lines.append(f"- {draft.identifier}")
        lines.append(f"  Title: {draft.title or 'Title not found.'}")
        lines.append(f"  Status: {draft.status or 'Status not found.'}")
    return "\n".join(lines)


def _format_discussion_summary(summary: DiscussionSummary) -> str:
    return summary.summary


def _format_meeting_updates(meeting_updates: MeetingUpdates) -> str:
    lines = ["Updates from last 2 IETF meetings:"]
    if not meeting_updates.updates:
        lines.append("- No IETF meeting updates found.")
        return "\n".join(lines)

    for update in meeting_updates.updates:
        lines.append(f"- {update.meeting}")
        lines.append("  Agenda:")
        if update.agendas:
            for agenda in update.agendas:
                lines.append(f"  - {agenda}")
        else:
            lines.append("  - Not found.")
        lines.append("  Minutes:")
        if update.minutes:
            for minute in update.minutes:
                lines.append(f"  - {minute}")
        else:
            lines.append("  - Not found.")
    return "\n".join(lines)


def _resolve_from_technology_flow() -> tuple[str, WorkingGroup | None]:
    while True:
        query = _read_nav_input("What technology area are you interested in? ")
        if query == NAV_BACK:
            return NAV_BACK, None
        if query == NAV_QUIT:
            return NAV_QUIT, None
        if not query:
            print("No technology area supplied.")
            continue

        matches = suggest_wgs_by_technology(
            query=query,
            top_k=10,
            require_all_terms=True,
        )
        print(_format_technology_matches(query, matches))
        if not matches:
            continue

        while True:
            choice = _read_nav_input(
                f"Select 1-{len(matches)} to continue with a WG: "
            )
            if choice == NAV_BACK:
                break
            if choice == NAV_QUIT:
                return NAV_QUIT, None
            if not choice.isdigit():
                print("Invalid selection.")
                continue

            selection = int(choice)
            if selection < 1 or selection > len(matches):
                print("Invalid selection.")
                continue

            selected = matches[selection - 1]
            return "ok", WorkingGroup(
                acronym=selected.acronym.lower(),
                name=selected.name,
            )


def _resolve_from_wg_name_flow() -> tuple[str, WorkingGroup | None]:
    while True:
        query = _read_nav_input("What Working Group are you interested in? ")
        if query == NAV_BACK:
            return NAV_BACK, None
        if query == NAV_QUIT:
            return NAV_QUIT, None
        if not query:
            print("No working group input supplied.")
            continue

        resolution: WgResolutionResult = resolve_wg_name(query)
        if resolution.matched:
            return "ok", resolution.matched

        suggestions = resolution.suggestions
        if not suggestions:
            print(f"No WG matched '{query}'.")
            continue

        print(f"No exact WG found for '{query}'. Did you mean:")
        for idx, candidate in enumerate(suggestions, start=1):
            print(f"{idx}. {candidate.acronym.upper()} - {candidate.name}")

        while True:
            choice = _read_nav_input(
                f"Select 1-{len(suggestions)} to continue: "
            )
            if choice == NAV_BACK:
                break
            if choice == NAV_QUIT:
                return NAV_QUIT, None
            if not choice.isdigit():
                print("Invalid selection.")
                continue

            selection = int(choice)
            if selection < 1 or selection > len(suggestions):
                print("Invalid selection.")
                continue
            return "ok", suggestions[selection - 1]


def _wg_feature_menu(wg: WorkingGroup) -> str:
    while True:
        print(f"\nMatched WG: {wg.acronym.upper()} - {wg.name}")
        print("Options:")
        print("1. Summary of WG")
        print("2. Active drafts")
        print("3. Draft discussions in a WG (last 3 months)")
        print("4. Updates from last 2 IETF meetings")
        print("b. Back")
        print("q. Quit")

        option = _read_nav_input("Select option: ")
        if option == NAV_BACK:
            return NAV_BACK
        if option == NAV_QUIT:
            return NAV_QUIT

        try:
            if option == "1":
                charter = get_wg_charter(wg.acronym)
                print(
                    f"\nComplete charter for {charter.wg_name} "
                    f"({charter.wg_id.upper()}):"
                )
                print(charter.charter_text)
            elif option == "2":
                drafts = get_wg_active_drafts(wg.acronym, limit=ACTIVE_DRAFTS_LIMIT)
                print("\n" + _format_active_drafts(drafts))
            elif option == "3":
                summary = get_wg_discussion_summary(wg.acronym, window_days=90)
                print("\n" + _format_discussion_summary(summary))
            elif option == "4":
                updates = get_wg_last_two_meeting_updates(wg.acronym)
                print("\n" + _format_meeting_updates(updates))
            else:
                print("Unsupported option.")
        except DatatrackerError as exc:
            print(f"Error: {exc}")


def main() -> None:
    print("IETF WG Agent")
    print("------------")

    while True:
        print("\nUser Types:")
        print("1. New engineer (technology onboarding)")
        print("2. Experienced engineer (known WG)")

        user_type = _read_nav_input("Select user type (1 or 2): ")
        if user_type == NAV_QUIT:
            print("Goodbye.")
            return
        if user_type == NAV_BACK:
            print("Already at top-level menu.")
            continue

        if user_type == "1":
            status, wg = _resolve_from_technology_flow()
        elif user_type == "2":
            status, wg = _resolve_from_wg_name_flow()
        else:
            print("Invalid user type selection.")
            continue

        if status == NAV_QUIT:
            print("Goodbye.")
            return
        if status == NAV_BACK or wg is None:
            continue

        menu_status = _wg_feature_menu(wg)
        if menu_status == NAV_QUIT:
            print("Goodbye.")
            return


if __name__ == "__main__":
    main()
