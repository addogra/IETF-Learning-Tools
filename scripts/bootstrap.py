#!/usr/bin/env python3
from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence, Tuple

MIN_PY = (3, 9)
PY310 = (3, 10)
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENV = ROOT / ".venv"
DEFAULT_MCP_VENV = ROOT / ".venv-mcp"


def _run(cmd: list[str], check: bool = True) -> int:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(ROOT))
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}")
    return proc.returncode


def _python_help() -> str:
    os_name = platform.system().lower()
    if os_name == "darwin":
        return "Install Python 3.9+ using Homebrew: brew install python@3.11"
    if os_name == "windows":
        return "Install Python 3.9+ using winget: winget install Python.Python.3.11"

    distro = ""
    try:
        release = Path("/etc/os-release")
        if release.exists():
            distro = release.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        pass

    if any(x in distro for x in ["ubuntu", "debian"]):
        return "Install Python with: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
    if any(x in distro for x in ["rhel", "centos", "fedora", "rocky", "almalinux"]):
        return "Install Python with: sudo dnf install -y python3 python3-pip"
    return "Install Python 3.9+ and ensure python3/pip are on PATH."


def _python_help_mcp() -> str:
    os_name = platform.system().lower()
    if os_name == "darwin":
        return "MCP requires Python 3.10+. Install with: brew install python@3.11"
    if os_name == "windows":
        return "MCP requires Python 3.10+. Install with: winget install Python.Python.3.11"

    distro = ""
    try:
        release = Path("/etc/os-release")
        if release.exists():
            distro = release.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        pass

    if any(x in distro for x in ["ubuntu", "debian"]):
        return "MCP requires Python 3.10+. Install with: sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip"
    if any(x in distro for x in ["rhel", "centos", "fedora", "rocky", "almalinux"]):
        return "MCP requires Python 3.10+. Install with: sudo dnf install -y python3.11 python3.11-pip"
    return "MCP requires Python 3.10+. Install Python 3.10+ and ensure it is on PATH."


def _venv_python(venv: Path) -> Path:
    if platform.system().lower() == "windows":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _activation_hint(venv: Path) -> str:
    if platform.system().lower() == "windows":
        return f"{venv}\\Scripts\\Activate.ps1"
    return f"source {venv}/bin/activate"


def _is_mcp_requested(extras: str) -> bool:
    parts = [p.strip().lower() for p in extras.split(",") if p.strip()]
    return "mcp" in parts


def _parse_version(raw: str) -> Optional[Tuple[int, int, int]]:
    bits = raw.strip().split(".")
    if len(bits) < 2:
        return None
    out: list[int] = []
    for b in bits[:3]:
        try:
            out.append(int("".join(ch for ch in b if ch.isdigit()) or "0"))
        except ValueError:
            return None
    while len(out) < 3:
        out.append(0)
    return (out[0], out[1], out[2])


def _probe_python(cmd: Sequence[str]) -> Optional[Tuple[int, int, int]]:
    try:
        proc = subprocess.run(
            [*cmd, "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except Exception:
        return None

    if proc.returncode != 0:
        return None
    return _parse_version(proc.stdout.strip())


def _find_python_for_mcp() -> Optional[list[str]]:
    candidates: list[list[str]] = []
    if platform.system().lower() == "windows":
        candidates.extend(
            [
                ["py", "-3.12"],
                ["py", "-3.11"],
                ["py", "-3.10"],
                ["python3.12"],
                ["python3.11"],
                ["python3.10"],
                ["python"],
            ]
        )
    else:
        candidates.extend(
            [
                ["python3.12"],
                ["python3.11"],
                ["python3.10"],
                ["python3"],
                ["python"],
            ]
        )

    for cmd in candidates:
        version = _probe_python(cmd)
        if version and version >= PY310:
            return cmd
    return None


def _select_python_command(
    *,
    requested_python: str,
    mcp_requested: bool,
    current_version: Tuple[int, int, int],
) -> Tuple[list[str], bool]:
    if requested_python:
        cmd = [requested_python]
        version = _probe_python(cmd)
        if not version:
            raise RuntimeError(f"Unable to execute requested python: {requested_python}")
        if version < MIN_PY:
            raise RuntimeError(
                f"Requested python {requested_python} is {version[0]}.{version[1]}; Python 3.9+ is required."
            )
        if mcp_requested and version < PY310:
            raise RuntimeError(
                f"Requested python {requested_python} is {version[0]}.{version[1]}; MCP requires Python 3.10+."
            )
        return cmd, False

    if mcp_requested and current_version < PY310:
        found = _find_python_for_mcp()
        if found:
            return found, True
    return [sys.executable], False


def _install_package(py: Path, extras: str, prefer_editable: bool) -> None:
    target = f".[{extras}]" if extras else "."

    if prefer_editable:
        rc = _run(
            [str(py), "-m", "pip", "install", "-e", target, "--no-build-isolation"],
            check=False,
        )
        if rc == 0:
            return
        print("Editable install failed; falling back to non-editable install.")

    _run([str(py), "-m", "pip", "install", target, "--no-build-isolation"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-platform setup for ietf-wg-agent")
    parser.add_argument(
        "--extras",
        default="full",
        help="Extras group to install (default: full). Use empty string for base.",
    )
    parser.add_argument(
        "--venv",
        default=str(DEFAULT_VENV),
        help=f"Virtualenv path (default: {DEFAULT_VENV})",
    )
    parser.add_argument(
        "--no-editable",
        action="store_true",
        help="Install non-editable package",
    )
    parser.add_argument(
        "--python",
        default="",
        help="Python executable for venv creation (example: python3.11).",
    )
    args = parser.parse_args()

    if sys.version_info < MIN_PY:
        req = ".".join(str(x) for x in MIN_PY)
        print(f"Python {req}+ required. Found: {sys.version.split()[0]}")
        print(_python_help())
        return 2

    extras = args.extras.strip()
    mcp_requested = _is_mcp_requested(extras)
    current = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)

    try:
        py_cmd, upgraded = _select_python_command(
            requested_python=args.python.strip(),
            mcp_requested=mcp_requested,
            current_version=current,
        )
    except RuntimeError as exc:
        print(str(exc))
        if mcp_requested:
            print(_python_help_mcp())
        return 4

    venv_str = args.venv
    if (
        mcp_requested
        and upgraded
        and Path(args.venv).expanduser().resolve() == DEFAULT_VENV.resolve()
    ):
        # Keep base .venv for 3.9-compatible CLI and create a dedicated MCP venv.
        venv_str = str(DEFAULT_MCP_VENV)
        print(f"Detected Python < 3.10 runtime; using MCP venv: {venv_str}")
        print(f"Selected interpreter for MCP: {' '.join(py_cmd)}")

    if mcp_requested and upgraded:
        print("MCP support requested and requires Python 3.10+.")
        print(f"Selected compatible interpreter: {' '.join(py_cmd)}")

    if mcp_requested and not upgraded and current < PY310 and py_cmd == [sys.executable]:
        print("MCP support requested but no Python 3.10+ interpreter was found on PATH.")
        print(_python_help_mcp())
        return 5

    venv = Path(venv_str).expanduser().resolve()
    if not venv.exists():
        _run([*py_cmd, "-m", "venv", str(venv)])

    vpy = _venv_python(venv)
    if not vpy.exists():
        print(f"Virtualenv python not found at {vpy}")
        return 3

    _run([str(vpy), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    # urllib3 v2 can emit LibreSSL/OpenSSL warnings on some Python 3.9 builds.
    # Force a compatible urllib3 for Python < 3.10 during setup.
    vpy_ver = _probe_python([str(vpy)]) or current
    if vpy_ver < PY310:
        _run([str(vpy), "-m", "pip", "install", "--upgrade", "urllib3<2"])

    _install_package(vpy, extras=extras, prefer_editable=not args.no_editable)

    print("\nSetup complete.")
    print(f"Activate environment: {_activation_hint(venv)}")
    print("Run app: ietf-wg-agent")
    print("Run daily job: ietf-wg-daily")
    if mcp_requested and vpy_ver >= PY310:
        print("Run MCP server: ietf-wg-mcp")
    elif mcp_requested:
        print("MCP was requested but is not available on this Python runtime.")
        print(_python_help_mcp())
    else:
        print("Run MCP server (Python 3.10+ only): ietf-wg-mcp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
