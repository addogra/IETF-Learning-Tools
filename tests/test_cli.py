from ietf_wg_agent import cli
from ietf_wg_agent.ietf import (
    DiscussionPost,
    DraftInfo,
    LastMeetingItem,
    MeetingUpdate,
    UpcomingAgendaItem,
    WgMatch,
    WorkingGroup,
)


def _feed_inputs(monkeypatch, values):
    it = iter(values)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(it))


def test_cli_option_1_summary_flow(monkeypatch, capsys):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",  # email
            "LSR",               # wg input
            "1",                 # option
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: [wg])
    monkeypatch.setattr(cli, "resolve_working_group", lambda _q, _groups: wg)
    monkeypatch.setattr(cli, "fetch_charter_text", lambda _ac: "charter text")
    monkeypatch.setattr(cli, "summarize_charter", lambda _txt: "summary output")

    calls = []

    def _fake_register(user_id: str, acronym: str):
        calls.append((user_id, acronym))

    monkeypatch.setattr(cli, "register_daily_update", _fake_register)

    cli.main()
    out = capsys.readouterr().out

    assert "Matched WG: LSR - Link State Routing" in out
    assert "summary output" in out
    assert calls == []


def test_cli_option_2_recent_activity_flow(monkeypatch, capsys):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",  # email
            "LSR",               # wg input
            "2",                 # option
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: [wg])
    monkeypatch.setattr(cli, "resolve_working_group", lambda _q, _groups: wg)
    monkeypatch.setattr(
        cli,
        "fetch_top_active_drafts",
        lambda _ac, limit=5: [
            DraftInfo(
                name="draft-ietf-lsr-example-00",
                title="Example Draft Title",
                status="WG Document: Proposed Standard Reviews",
                abstract="This draft defines an example extension.",
                url="https://datatracker.ietf.org/doc/draft-ietf-lsr-example-00/",
            )
        ],
    )

    calls = []

    def _fake_register(user_id: str, acronym: str):
        calls.append((user_id, acronym))

    monkeypatch.setattr(cli, "register_daily_update", _fake_register)

    cli.main()
    out = capsys.readouterr().out

    assert "Top 5 active drafts from WG documents" in out
    assert "draft-ietf-lsr-example-00" in out
    assert "Status: WG Document: Proposed Standard Reviews" in out
    assert "Abstract: This draft defines an example extension." in out
    assert calls == []


def test_cli_suggestion_selection_flow(monkeypatch, capsys):
    selected = WorkingGroup(acronym="lsvr", name="Link State Vector Routing")

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",  # email
            "LSRV",              # wrong wg input
            "1",                 # select suggested wg
            "1",                 # option
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: [selected])
    monkeypatch.setattr(cli, "resolve_working_group", lambda _q, _groups: None)
    monkeypatch.setattr(cli, "suggest_working_groups", lambda _q, _groups, limit=5: [selected])
    monkeypatch.setattr(cli, "fetch_charter_text", lambda _ac: "charter text")
    monkeypatch.setattr(cli, "summarize_charter", lambda _txt: "summary output")

    cli.main()
    out = capsys.readouterr().out

    assert "Did you mean" in out
    assert "1. LSVR - Link State Vector Routing" in out
    assert "Selected WG: LSVR - Link State Vector Routing" in out
    assert "summary output" in out


def test_cli_option_3_discussions_flow(monkeypatch, capsys):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",  # email
            "LSR",               # wg input
            "3",                 # option
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: [wg])
    monkeypatch.setattr(cli, "resolve_working_group", lambda _q, _groups: wg)
    monkeypatch.setattr(
        cli,
        "fetch_wg_discussions_last_months",
        lambda _ac, months=3: [
            DiscussionPost(
                date="2099-01-10",
                subject="Thread A",
                author="Alice",
                url="https://mailarchive.ietf.org/arch/msg/lsr/abc123/",
            )
        ],
    )

    calls = []

    def _fake_register(user_id: str, acronym: str):
        calls.append((user_id, acronym))

    monkeypatch.setattr(cli, "register_daily_update", _fake_register)

    cli.main()
    out = capsys.readouterr().out

    assert "Draft discussions summary (last 3 months):" in out
    assert "Total discussion posts: 1" in out
    assert "Thread A" in out
    assert calls == []


def test_cli_option_4_meeting_updates_flow(monkeypatch, capsys):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",  # email
            "LSR",               # wg input
            "4",                 # option
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: [wg])
    monkeypatch.setattr(cli, "resolve_working_group", lambda _q, _groups: wg)
    monkeypatch.setattr(
        cli,
        "fetch_updates_from_last_two_meetings",
        lambda _ac, limit=2: [
            MeetingUpdate(
                meeting="IETF 122",
                agendas=["https://datatracker.ietf.org/meeting/122/materials/agenda-wg-lsr"],
                minutes=["https://datatracker.ietf.org/meeting/122/materials/minutes-wg-lsr"],
            )
        ],
    )

    calls = []

    def _fake_register(user_id: str, acronym: str):
        calls.append((user_id, acronym))

    monkeypatch.setattr(cli, "register_daily_update", _fake_register)

    cli.main()
    out = capsys.readouterr().out
    assert "Updates from last 2 IETF meetings:" in out
    assert "IETF 122" in out
    assert "agenda-wg-lsr" in out
    assert "minutes-wg-lsr" in out
    assert calls == []


def test_cli_option_5_daily_updates_flow(monkeypatch, capsys):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",  # email
            "LSR",               # wg input
            "5",                 # option
            "n",                 # skip register
            "y",                 # start scheduler
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: [wg])
    monkeypatch.setattr(cli, "resolve_working_group", lambda _q, _groups: wg)
    monkeypatch.setattr(
        cli,
        "fetch_wg_discussions_last_day",
        lambda _ac, days=1: [
            DiscussionPost(
                date="2099-01-10",
                subject="Recent thread",
                author="Alice",
                url="https://mailarchive.ietf.org/arch/msg/lsr/new1/",
            )
        ],
    )
    monkeypatch.setattr(
        cli,
        "_start_daily_updates_scheduler",
        lambda: "Daily updates scheduler started (pid=1234).",
    )

    cli.main()
    out = capsys.readouterr().out
    assert "Draft discussions summary (last 1 day):" in out
    assert "Recent thread" in out
    assert "Daily updates scheduler started (pid=1234)." in out


def test_cli_option_6_upcoming_agenda_flow(monkeypatch, capsys):
    groups = [
        WorkingGroup(acronym="lsr", name="Link State Routing"),
        WorkingGroup(acronym="bess", name="BGP Enabled ServiceS"),
    ]
    wg = groups[0]

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",  # email
            "LSR",               # wg input
            "6",                 # option
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: groups)
    monkeypatch.setattr(cli, "resolve_working_group", lambda _q, _groups: wg)
    monkeypatch.setattr(
        cli,
        "fetch_upcoming_ietf_agenda",
        lambda _groups: (
            "IETF 122 - March 15, 2027 - March 21, 2027 - Yokohama, Japan",
            [
                UpcomingAgendaItem(
                    wg_acronym="lsr",
                    wg_name="Link State Routing",
                    agenda_url="https://datatracker.ietf.org/meeting/122/materials/agenda-lsr",
                    agenda_summary="Review milestones and draft status updates.",
                )
            ],
        ),
    )

    calls = []

    def _fake_register(user_id: str, acronym: str):
        calls.append((user_id, acronym))

    monkeypatch.setattr(cli, "register_daily_update", _fake_register)

    cli.main()
    out = capsys.readouterr().out
    assert "IETF 122 - March 15, 2027 - March 21, 2027 - Yokohama, Japan" in out
    assert "Working Group Link State Routing (LSR)" in out
    assert "Review milestones and draft status updates." in out
    assert calls == []


def test_cli_option_7_last_meeting_summary_flow(monkeypatch, capsys):
    groups = [
        WorkingGroup(acronym="lsr", name="Link State Routing"),
        WorkingGroup(acronym="bess", name="BGP Enabled ServiceS"),
    ]
    wg = groups[0]

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",  # email
            "LSR",               # wg input
            "7",                 # option
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: groups)
    monkeypatch.setattr(cli, "resolve_working_group", lambda _q, _groups: wg)
    monkeypatch.setattr(
        cli,
        "fetch_summary_of_last_ietf_meeting",
        lambda _groups: (
            "IETF 121 - March 15, 2024 - March 21, 2024 - Brisbane, Australia",
            [
                LastMeetingItem(
                    wg_acronym="lsr",
                    wg_name="Link State Routing",
                    agenda_url="https://datatracker.ietf.org/meeting/121/materials/agenda-lsr",
                    minutes_url="https://datatracker.ietf.org/meeting/121/materials/minutes-lsr",
                    minutes_summary="Reviewed milestones and progressed two drafts.",
                )
            ],
        ),
    )

    calls = []

    def _fake_register(user_id: str, acronym: str):
        calls.append((user_id, acronym))

    monkeypatch.setattr(cli, "register_daily_update", _fake_register)

    cli.main()
    out = capsys.readouterr().out
    assert "IETF 121 - March 15, 2024 - March 21, 2024 - Brisbane, Australia" in out
    assert "Working Group Link State Routing (LSR)" in out
    assert "Reviewed milestones and progressed two drafts." in out
    assert calls == []


def test_cli_technology_onboarding_flow(monkeypatch, capsys):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")

    _feed_inputs(
        monkeypatch,
        [
            "user@example.com",      # email
            "tech",                  # onboarding mode trigger
            "bgp-ls flex-algo",      # technology query
            "1",                     # select top match
            "1",                     # option
        ],
    )

    monkeypatch.setattr(cli, "fetch_working_groups", lambda: [wg])
    monkeypatch.setattr(
        cli,
        "suggest_wgs_by_technology",
        lambda _query, top_k=10, require_all_terms=True: [
            WgMatch(
                acronym="LSR",
                name="Link State Routing",
                score=0.93,
                justification="Matched terms: bgp, flex, algo",
            )
        ],
    )
    monkeypatch.setattr(cli, "fetch_charter_text", lambda _ac: "charter text")
    monkeypatch.setattr(cli, "summarize_charter", lambda _txt: "summary output")

    cli.main()
    out = capsys.readouterr().out

    assert "Technology onboarding results for 'bgp-ls flex-algo':" in out
    assert "1. LSR - Link State Routing (score=0.9300)" in out
    assert "Selected WG: LSR - Link State Routing" in out
    assert "summary output" in out
