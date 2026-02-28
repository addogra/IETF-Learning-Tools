from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_bootstrap_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "bootstrap.py"
    spec = importlib.util.spec_from_file_location("bootstrap_module", str(script))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_is_mcp_requested_parsing():
    b = _load_bootstrap_module()
    assert b._is_mcp_requested("mcp") is True
    assert b._is_mcp_requested("dev,mcp") is True
    assert b._is_mcp_requested("full") is False
    assert b._is_mcp_requested("") is False


def test_parse_version_handles_basic_values():
    b = _load_bootstrap_module()
    assert b._parse_version("3.10.2") == (3, 10, 2)
    assert b._parse_version("3.11") == (3, 11, 0)
    assert b._parse_version("not-a-version") is None


def test_select_python_command_autoupgrades_for_mcp(monkeypatch):
    b = _load_bootstrap_module()
    monkeypatch.setattr(b, "_find_python_for_mcp", lambda: ["python3.11"])
    cmd, upgraded = b._select_python_command(
        requested_python="",
        mcp_requested=True,
        current_version=(3, 9, 6),
    )
    assert cmd == ["python3.11"]
    assert upgraded is True


def test_select_python_command_uses_current_when_not_mcp():
    b = _load_bootstrap_module()
    cmd, upgraded = b._select_python_command(
        requested_python="",
        mcp_requested=False,
        current_version=(3, 9, 6),
    )
    assert cmd == [sys.executable]
    assert upgraded is False
