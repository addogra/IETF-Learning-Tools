import importlib
import sys
import types

import pytest


class FakeFastMCP:
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.run_called = False
        self.transport = None

    def tool(self):
        def _decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return _decorator

    def run(self, transport: str = "stdio"):
        self.run_called = True
        self.transport = transport


def _reload_server_module(with_fake_mcp: bool):
    # Reset module cache so decorators execute under selected MCP availability.
    sys.modules.pop("ietf_wg_agent.server", None)

    if with_fake_mcp:
        fake_pkg = types.ModuleType("mcp")
        fake_server_pkg = types.ModuleType("mcp.server")
        fake_fastmcp_mod = types.ModuleType("mcp.server.fastmcp")
        fake_fastmcp_mod.FastMCP = FakeFastMCP

        sys.modules["mcp"] = fake_pkg
        sys.modules["mcp.server"] = fake_server_pkg
        sys.modules["mcp.server.fastmcp"] = fake_fastmcp_mod
    else:
        sys.modules.pop("mcp", None)
        sys.modules.pop("mcp.server", None)
        sys.modules.pop("mcp.server.fastmcp", None)

    return importlib.import_module("ietf_wg_agent.server")


def test_server_main_raises_when_mcp_not_installed():
    server = _reload_server_module(with_fake_mcp=False)
    if server.FastMCP is not None:
        pytest.skip("Real MCP installed in environment; skip missing-MCP behavior test")

    with pytest.raises(RuntimeError):
        server.main()


def test_server_registers_and_runs_with_fake_mcp():
    server = _reload_server_module(with_fake_mcp=True)

    expected_tools = {
        "find_working_group",
        "technology_onboarding",
        "summary_of_wg",
        "register_wg_daily_update",
        "active_drafts_and_recent_rfcs",
        "active_drafts",
        "draft_discussions_summary",
        "daily_updates_summary",
        "updates_from_last_2_ietf_meetings",
        "agenda_of_upcoming_ietf_meeting",
        "summary_of_last_ietf_meeting",
        "run_daily_summary_now",
        "run_daily_updates_summary_now",
        "send_daily_emails_now",
        "send_daily_updates_now",
    }

    assert expected_tools.issubset(set(server.mcp.tools.keys()))

    server.main()
    assert server.mcp.run_called is True
    assert server.mcp.transport == "stdio"


def test_summary_of_wg_returns_complete_charter(monkeypatch):
    server = _reload_server_module(with_fake_mcp=True)

    class _WG:
        def __init__(self, acronym: str, name: str):
            self.acronym = acronym
            self.name = name

    monkeypatch.setattr(
        server,
        "fetch_working_groups",
        lambda: [_WG("lsr", "Link State Routing")],
    )
    monkeypatch.setattr(
        server,
        "resolve_working_group",
        lambda query, groups: _WG("lsr", "Link State Routing"),
    )
    monkeypatch.setattr(
        server,
        "fetch_charter_text",
        lambda acronym: "Complete charter text without truncation.",
    )

    out = server.mcp.tools["summary_of_wg"]("LSR")
    assert "Complete charter for Link State Routing (LSR):" in out
    assert "Complete charter text without truncation." in out


def test_active_drafts_tool_uses_limit_10(monkeypatch):
    server = _reload_server_module(with_fake_mcp=True)

    class _WG:
        def __init__(self, acronym: str, name: str):
            self.acronym = acronym
            self.name = name

    monkeypatch.setattr(
        server,
        "fetch_working_groups",
        lambda: [_WG("lsr", "Link State Routing")],
    )
    monkeypatch.setattr(
        server,
        "resolve_working_group",
        lambda query, groups: _WG("lsr", "Link State Routing"),
    )

    limits: list[int] = []

    class _Draft:
        def __init__(self):
            self.name = "draft-ietf-lsr-example-00"
            self.title = "Example"
            self.status = "WG Document"
            self.abstract = "Abstract"
            self.url = "https://datatracker.ietf.org/doc/draft-ietf-lsr-example-00/"

    def _fake_fetch(acronym: str, limit: int = 5):
        limits.append(limit)
        return [_Draft()]

    monkeypatch.setattr(server, "fetch_top_active_drafts", _fake_fetch)

    out = server.mcp.tools["active_drafts"]("LSR")
    assert limits == [10]
    assert "draft-ietf-lsr-example-00" in out


def test_updates_from_last_2_ietf_meetings_formats_agenda_and_minutes(monkeypatch):
    server = _reload_server_module(with_fake_mcp=True)

    class _WG:
        def __init__(self, acronym: str, name: str):
            self.acronym = acronym
            self.name = name

    class _Update:
        def __init__(self, meeting: str, agendas: list[str], minutes: list[str]):
            self.meeting = meeting
            self.agendas = agendas
            self.minutes = minutes

    monkeypatch.setattr(
        server,
        "fetch_working_groups",
        lambda: [_WG("lsr", "Link State Routing")],
    )
    monkeypatch.setattr(
        server,
        "resolve_working_group",
        lambda query, groups: _WG("lsr", "Link State Routing"),
    )
    monkeypatch.setattr(
        server,
        "fetch_updates_from_last_two_meetings",
        lambda acronym, limit=2: [
            _Update(
                meeting="IETF 122",
                agendas=["https://datatracker.ietf.org/meeting/122/materials/agenda-wg-lsr"],
                minutes=["https://datatracker.ietf.org/meeting/122/materials/minutes-wg-lsr"],
            ),
            _Update(
                meeting="IETF 121",
                agendas=[],
                minutes=["https://datatracker.ietf.org/meeting/121/materials/minutes-wg-lsr"],
            ),
        ],
    )

    out = server.mcp.tools["updates_from_last_2_ietf_meetings"]("LSR")
    assert "WG: LSR - Link State Routing" in out
    assert "Updates from last 2 IETF meetings:" in out
    assert "Agendas:" in out
    assert "Minutes:" in out
    assert "IETF 122" in out


def test_agenda_of_upcoming_ietf_meeting_output_format(monkeypatch):
    server = _reload_server_module(with_fake_mcp=True)

    class _WG:
        def __init__(self, acronym: str, name: str):
            self.acronym = acronym
            self.name = name

    monkeypatch.setattr(
        server,
        "fetch_working_groups",
        lambda: [_WG("lsr", "Link State Routing"), _WG("bess", "BGP Enabled ServiceS")],
    )
    monkeypatch.setattr(
        server,
        "fetch_upcoming_ietf_agenda",
        lambda _groups: (
            "Next IETF events planned and dates and location:\n"
            "- IETF 125 - Dates 2026-03-14 - Place Shenzhen, CN\n"
            "- IETF 126 - Dates 2026-07-18 - Place Vienna, AT\n"
            "- IETF 127 - Dates 2026-11-14 - Place San Francisco, US\n\n"
            "Important details (IETF 125):\n"
            "- IETF Online Registration Opens: 2025-09-22\n"
            "- Final agenda to be published: 2026-03-09\n"
            "- Agenda link - for IETF-125: https://datatracker.ietf.org/meeting/125/agenda.txt\n"
            "- Internet-Draft submission cut-off: 2026-03-02\n"
            "- Registration cancellation cut-off: 2026-03-16",
            [],
        ),
    )

    out = server.mcp.tools["agenda_of_upcoming_ietf_meeting"]()
    assert "Next IETF events planned and dates and location:" in out
    assert "IETF 125 - Dates 2026-03-14 - Place Shenzhen, CN" in out
    assert "Important details (IETF 125):" in out
    assert "Agenda link - for IETF-125: https://datatracker.ietf.org/meeting/125/agenda.txt" in out
    assert "Working Group " not in out
    assert "meeting/125/agenda.txt" in out
