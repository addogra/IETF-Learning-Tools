from __future__ import annotations

from pathlib import Path
import sys

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

MIN_PY = (3, 9)

if sys.version_info < MIN_PY:
    version = ".".join(str(part) for part in MIN_PY)
    raise SystemExit(
        f"ietf-wg-agent requires Python {version}+; found {sys.version.split()[0]}"
    )


class _PostInstallMixin:
    def _print_next_steps(self) -> None:
        print("\n[ietf-wg-agent] Installation complete.")
        print("Next steps:")
        print("1) Run interactive app: ietf-wg-agent")
        print("2) Run daily summary+email: ietf-wg-daily")
        print("3) Optional MCP support: pip install -e '.[mcp]'")
        print("4) Configure SMTP env vars before daily email delivery")


class PostInstallCommand(install, _PostInstallMixin):
    def run(self):
        install.run(self)
        self._print_next_steps()


class PostDevelopCommand(develop, _PostInstallMixin):
    def run(self):
        develop.run(self)
        self._print_next_steps()


README = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="ietf-wg-agent",
    version="0.1.0",
    description="MCP/agent for IETF working-group charter summaries and daily updates",
    long_description=README,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.31.0,<3.0.0",
        "beautifulsoup4>=4.12.3,<5.0.0",
        "urllib3<2; python_version < '3.10'",
    ],
    extras_require={
        "mcp": ["mcp>=1.0.0; python_version >= '3.10'"],
        "dev": ["pytest>=7.4.0,<9.0.0"],
        "full": [
            "mcp>=1.0.0; python_version >= '3.10'",
            "pytest>=7.4.0,<9.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ietf-wg-agent=ietf_wg_agent.cli:main",
            "ietf-wg-mcp=ietf_wg_agent.server:main",
            "ietf-wg-daily=ietf_wg_agent.daily:main",
            "ietf-wg-daily-updates=ietf_wg_agent.discussion_scheduler:main",
            "ietf-wg-daily-updates-scheduler=ietf_wg_agent.discussion_scheduler:main",
        ]
    },
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
    },
)
