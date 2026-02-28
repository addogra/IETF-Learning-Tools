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
