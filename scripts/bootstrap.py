#!/usr/bin/env python3
# Author: Aditya Dogra
from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path

MIN_PY = (3, 9)
PY310 = (3, 10)
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENV = ROOT / ".venv"


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


def _venv_python(venv: Path) -> Path:
    if platform.system().lower() == "windows":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _activation_hint(venv: Path) -> str:
    if platform.system().lower() == "windows":
        return f"{venv}\\Scripts\\Activate.ps1"
    return f"source {venv}/bin/activate"


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
    args = parser.parse_args()

    if sys.version_info < MIN_PY:
        req = ".".join(str(x) for x in MIN_PY)
        print(f"Python {req}+ required. Found: {sys.version.split()[0]}")
        print(_python_help())
        return 2

    venv = Path(args.venv).expanduser().resolve()
    if not venv.exists():
        _run([sys.executable, "-m", "venv", str(venv)])

    vpy = _venv_python(venv)
    if not vpy.exists():
        print(f"Virtualenv python not found at {vpy}")
        return 3

    _run([str(vpy), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    # urllib3 v2 can emit LibreSSL/OpenSSL warnings on some Python 3.9 builds.
    # Force a compatible urllib3 for Python < 3.10 during setup.
    if sys.version_info < PY310:
        _run([str(vpy), "-m", "pip", "install", "--upgrade", "urllib3<2"])

    extras = args.extras.strip()
    _install_package(vpy, extras=extras, prefer_editable=not args.no_editable)

    print("\nSetup complete.")
    print(f"Activate environment: {_activation_hint(venv)}")
    print("Run app: ietf-wg-agent")
    print("Run daily job: ietf-wg-daily")
    print("Run MCP server: ietf-wg-mcp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
