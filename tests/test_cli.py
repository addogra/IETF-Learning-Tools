from ietf_wg_agent import cli
from ietf_wg_agent.ietf import (
    DiscussionSummary,
    DraftResult,
    WgMatch,
    WgResolutionResult,
    WorkingGroup,
)


def _feed_inputs(monkeypatch, values):
    it = iter(values)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(it))


def test_cli_new_engineer_technology_onboarding_summary_then_quit(monkeypatch, capsys):
    _feed_inputs(
        monkeypatch,
        [
            "1",                    # user type: new engineer
            "OSPF security",        # technology query
            "1",                    # select first WG match
            "1",                    # option: summary
            "q",                    # quit from feature menu
        ],
    )

    monkeypatch.setattr(
        cli,
        "suggest_wgs_by_technology",
        lambda query, top_k=10, require_all_terms=True: [
            WgMatch(
                acronym="LSR",
                name="Link State Routing",
                score=0.91,
                justification="Matched terms: ospf, security",
            )
        ],
    )
    monkeypatch.setattr(
        cli,
        "get_wg_charter",
        lambda _wg_id: type(
            "_Charter",
            (),
            {
                "wg_id": "lsr",
                "wg_name": "Link State Routing",
                "charter_text": "Complete charter text without truncation.",
            },
        )(),
    )

    cli.main()
    out = capsys.readouterr().out

    assert "Technology onboarding results for 'OSPF security':" in out
    assert "1. LSR - Link State Routing (score=0.9100)" in out
    assert "Complete charter for Link State Routing (LSR):" in out
    assert "Complete charter text without truncation." in out
    assert "Goodbye." in out


def test_cli_type_a_prompt_text_is_clean_and_minimal(monkeypatch, capsys):
    prompts: list[str] = []
    values = iter(
        [
            "1",              # user type: new engineer
            "BGP TLS",        # technology query
            "1",              # select first WG
            "q",              # quit in feature menu
        ]
    )

    def _fake_input(prompt=""):
        prompts.append(prompt)
        return next(values)

    monkeypatch.setattr("builtins.input", _fake_input)
    monkeypatch.setattr(
        cli,
        "suggest_wgs_by_technology",
        lambda query, top_k=10, require_all_terms=True: [
            WgMatch(
                acronym="IDR",
                name="Inter-Domain Routing",
                score=0.87,
                justification="Matched terms: bgp, tls",
            )
        ],
    )

    cli.main()
    out = capsys.readouterr().out

    assert prompts[0] == "Select user type (1 or 2): "
    assert prompts[1] == "What technology area are you interested in? "
    assert prompts[2] == "Select 1-1 to continue with a WG: "
    assert prompts[3] == "Select option: "
    assert "or 'b' to go back, 'q' to quit" not in out
    assert (
        "User Types:\n1. New engineer (technology onboarding)\n"
        "2. Experienced engineer (known WG)\nq. Quit"
    ) not in out


def test_cli_experienced_engineer_resolution_with_back_to_previous_menu(monkeypatch, capsys):
    _feed_inputs(
        monkeypatch,
        [
            "2",            # user type: experienced engineer
            "LSR",          # WG input
            "1",            # option: summary
            "b",            # back from feature menu
            "q",            # quit from user type menu
        ],
    )

    monkeypatch.setattr(
        cli,
        "resolve_wg_name",
        lambda _query: WgResolutionResult(
            query="LSR",
            matched=WorkingGroup(acronym="lsr", name="Link State Routing"),
            suggestions=[],
        ),
    )
    monkeypatch.setattr(
        cli,
        "get_wg_charter",
        lambda _wg_id: type(
            "_Charter",
            (),
            {
                "wg_id": "lsr",
                "wg_name": "Link State Routing",
                "charter_text": "Full charter payload.",
            },
        )(),
    )

    cli.main()
    out = capsys.readouterr().out

    assert "Matched WG: LSR - Link State Routing" in out
    assert "Full charter payload." in out
    assert out.count("User Types:") >= 2
    assert "Goodbye." in out


def test_cli_experienced_engineer_suggestion_selection(monkeypatch, capsys):
    _feed_inputs(
        monkeypatch,
        [
            "2",            # user type: experienced engineer
            "LSRV",         # WG input
            "1",            # select first suggestion
            "1",            # option: summary
            "q",            # quit
        ],
    )

    suggestion = WorkingGroup(acronym="lsvr", name="Link State Vector Routing")
    monkeypatch.setattr(
        cli,
        "resolve_wg_name",
        lambda _query: WgResolutionResult(
            query="LSRV",
            matched=None,
            suggestions=[suggestion],
        ),
    )
    monkeypatch.setattr(
        cli,
        "get_wg_charter",
        lambda _wg_id: type(
            "_Charter",
            (),
            {
                "wg_id": "lsvr",
                "wg_name": "Link State Vector Routing",
                "charter_text": "Complete charter text.",
            },
        )(),
    )

    cli.main()
    out = capsys.readouterr().out

    assert "No exact WG found for 'LSRV'. Did you mean:" in out
    assert "1. LSVR - Link State Vector Routing" in out
    assert "Complete charter text." in out


def test_cli_active_drafts_returns_all(monkeypatch, capsys):
    _feed_inputs(
        monkeypatch,
        [
            "2",          # user type
            "LSR",        # WG input
            "2",          # option: active drafts
            "q",          # quit
        ],
    )

    monkeypatch.setattr(
        cli,
        "resolve_wg_name",
        lambda _query: WgResolutionResult(
            query="LSR",
            matched=WorkingGroup(acronym="lsr", name="Link State Routing"),
            suggestions=[],
        ),
    )

    captured_limits: list[int] = []

    def _fake_get_wg_active_drafts(_wg_id: str, limit: int = 5):
        captured_limits.append(limit)
        return [
            DraftResult(
                identifier="draft-ietf-lsr-example-00",
                title="Example 00",
                status="WG Document",
                abstract="",
                url="",
            ),
            DraftResult(
                identifier="draft-ietf-lsr-example-01",
                title="Example 01",
                status="In WG Last Call",
                abstract="",
                url="",
            ),
        ]

    monkeypatch.setattr(cli, "get_wg_active_drafts", _fake_get_wg_active_drafts)

    cli.main()
    out = capsys.readouterr().out

    assert captured_limits == [10]
    assert "Active drafts:" in out
    assert "draft-ietf-lsr-example-00" in out
    assert "draft-ietf-lsr-example-01" in out
    assert "Status: WG Document" in out


def test_cli_draft_discussions_last_3_months(monkeypatch, capsys):
    _feed_inputs(
        monkeypatch,
        [
            "2",          # user type
            "LSR",        # WG input
            "3",          # option: draft discussions
            "q",          # quit
        ],
    )

    monkeypatch.setattr(
        cli,
        "resolve_wg_name",
        lambda _query: WgResolutionResult(
            query="LSR",
            matched=WorkingGroup(acronym="lsr", name="Link State Routing"),
            suggestions=[],
        ),
    )

    calls: list[int] = []

    def _fake_discussions(_wg_id: str, window_days: int = 90):
        calls.append(window_days)
        return DiscussionSummary(
            wg_id="lsr",
            wg_name="Link State Routing",
            window_days=90,
            post_count=2,
            summary="Draft discussions summary (last 3 months):\n- Total discussion posts: 2",
            posts=[],
        )

    monkeypatch.setattr(cli, "get_wg_discussion_summary", _fake_discussions)

    cli.main()
    out = capsys.readouterr().out

    assert calls == [90]
    assert "Draft discussions summary (last 3 months):" in out
    assert "Total discussion posts: 2" in out
