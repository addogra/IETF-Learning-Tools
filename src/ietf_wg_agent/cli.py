from __future__ import annotations

"""Interactive CLI orchestration.

Current start-flow scope:
1) Select user type (new engineer vs experienced engineer).
2) Resolve WG via technology onboarding or WG-name resolution.
3) Execute one feature action:
   - complete charter output,
   - all active drafts output.
"""

from ietf_wg_agent.ietf import (
    DatatrackerError,
    DraftResult,
    WgMatch,
    WorkingGroup,
    get_wg_active_drafts,
    get_wg_charter,
    resolve_wg_name,
    suggest_wgs_by_technology,
)


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


def _resolve_from_technology_flow() -> WorkingGroup:
    query = input("What technology area are you interested in? ").strip()
    if not query:
        raise DatatrackerError("No technology area supplied.")

    matches = suggest_wgs_by_technology(
        query=query,
        top_k=10,
        require_all_terms=True,
    )
    print(_format_technology_matches(query, matches))
    if not matches:
        raise DatatrackerError("No WG matched the technology query.")

    choice = input(
        f"Select 1-{len(matches)} to continue with a WG, "
        "or press Enter to cancel: "
    ).strip()
    if not choice:
        raise DatatrackerError("Selection cancelled.")
    if not choice.isdigit():
        raise DatatrackerError("Invalid selection.")

    selection = int(choice)
    if selection < 1 or selection > len(matches):
        raise DatatrackerError("Invalid selection.")

    selected = matches[selection - 1]
    return WorkingGroup(acronym=selected.acronym.lower(), name=selected.name)


def _resolve_from_wg_name_flow() -> WorkingGroup:
    query = input("What Working Group are you interested in? ").strip()
    if not query:
        raise DatatrackerError("No working group input supplied.")

    resolution = resolve_wg_name(query)
    if resolution.matched:
        return resolution.matched

    suggestions = resolution.suggestions
    if not suggestions:
        raise DatatrackerError(f"No WG matched '{query}'.")

    print(f"No exact WG found for '{query}'. Did you mean:")
    for idx, candidate in enumerate(suggestions, start=1):
        print(f"{idx}. {candidate.acronym.upper()} - {candidate.name}")

    choice = input(
        f"Select 1-{len(suggestions)} to continue, or press Enter to cancel: "
    ).strip()
    if not choice:
        raise DatatrackerError("Selection cancelled.")
    if not choice.isdigit():
        raise DatatrackerError("Invalid selection.")

    selection = int(choice)
    if selection < 1 or selection > len(suggestions):
        raise DatatrackerError("Invalid selection.")
    return suggestions[selection - 1]


def main() -> None:
    print("IETF WG Agent")
    print("------------")
    print("User Types:")
    print("1. New engineer (technology onboarding)")
    print("2. Experienced engineer (known WG)")

    try:
        user_type = input("Select user type (1 or 2): ").strip()
        if user_type == "1":
            wg = _resolve_from_technology_flow()
        elif user_type == "2":
            wg = _resolve_from_wg_name_flow()
        else:
            print("Invalid user type selection.")
            return

        print(f"Matched WG: {wg.acronym.upper()} - {wg.name}")
        print("\nOptions:")
        print("1. Summary of WG")
        print("2. Active drafts")
        option = input("Select option: ").strip()

        if option == "1":
            charter = get_wg_charter(wg.acronym)
            print(f"\nComplete charter for {charter.wg_name} ({charter.wg_id.upper()}):")
            print(charter.charter_text)
        elif option == "2":
            drafts = get_wg_active_drafts(wg.acronym, limit=0)
            print("\n" + _format_active_drafts(drafts))
        else:
            print("Unsupported option.")

    except DatatrackerError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
