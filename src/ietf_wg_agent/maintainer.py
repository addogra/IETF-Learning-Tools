from __future__ import annotations

"""Maintainer-only operations for charter DB lifecycle and repo hygiene checks."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Optional

from ietf_wg_agent.ietf import (
    DatatrackerError,
    DbMetadata,
    RebuildResult,
    get_db_metadata,
    rebuild_wg_charter_db,
)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _required_artifact_relpaths() -> list[str]:
    return [
        "AGENTS.md",
        "ARCHITECTURE.md",
        "README.md",
        "requirements.txt",
        "docs/DESIGN.md",
        "docs/QUALITY_SCORE.md",
        "docs/RELIABILITY.md",
        "docs/SECURITY.md",
        "docs/product-specs/new-user-onboarding.md",
        "docs/exec-plans/active/2026-02-28-requirements-parity-phase-1.md",
        "docs/exec-plans/tech-debt-tracker.md",
        "SKILLS.md",
    ]


def _module_doc_to_source_relpaths() -> dict[str, str]:
    return {
        "docs/design-docs/modules/cli-module.md": "src/ietf_wg_agent/cli.py",
        "docs/design-docs/modules/ietf-module.md": "src/ietf_wg_agent/ietf.py",
        "docs/design-docs/modules/summarizer-module.md": "src/ietf_wg_agent/summarizer.py",
        "docs/design-docs/modules/subscriptions-module.md": "src/ietf_wg_agent/subscriptions.py",
        "docs/design-docs/modules/notifier-module.md": "src/ietf_wg_agent/notifier.py",
        "docs/design-docs/modules/daily-module.md": "src/ietf_wg_agent/daily.py",
        "docs/design-docs/modules/server-module.md": "src/ietf_wg_agent/server.py",
        "docs/design-docs/modules/maintainer-module.md": "src/ietf_wg_agent/maintainer.py",
    }


def _required_api_contract_names() -> list[str]:
    return [
        "rebuild_wg_charter_db",
        "get_db_metadata",
        "resolve_wg_name",
        "suggest_wgs_by_technology",
        "get_wg_charter",
        "get_wg_active_drafts",
        "get_wg_discussion_summary",
        "get_wg_last_two_meeting_updates",
        "get_upcoming_ietf_agenda_summary",
        "get_last_ietf_meeting_summary",
        "track_draft_or_rfc",
        "run_daily_wg_update",
        "schedule_daily_updates",
    ]


def _extract_skill_paths(skills_index_text: str) -> list[str]:
    paths: list[str] = []
    for line in skills_index_text.splitlines():
        match = re.match(r"\|\s*`[^`]+`\s*\|\s*`([^`]+)`\s*\|", line)
        if match:
            paths.append(match.group(1))
    return paths


def _check_api_contract_doc_alignment(
    repo_root: Path, api_presence: dict[str, bool]
) -> list[str]:
    issues: list[str] = []
    rel = "docs/design-docs/internal-api-contract.md"
    path = repo_root / rel
    if not path.exists():
        return [f"Missing API contract doc: {rel}"]

    text = path.read_text(encoding="utf-8")
    for name, present in api_presence.items():
        pattern = re.compile(
            rf"\|[^|\n]*\|\s*`{re.escape(name)}`\s*\|[^|\n]*\|\s*(Implemented|Pending)\s*\|",
            flags=re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            issues.append(f"API contract doc missing row for function: {name}")
            continue

        status = match.group(1).strip().lower()
        if present and status != "implemented":
            issues.append(
                f"API contract doc status mismatch for {name}: "
                "code=implemented doc!=Implemented"
            )
        if not present and status == "implemented":
            issues.append(
                f"API contract doc status mismatch for {name}: "
                "code=missing doc=Implemented"
            )
    return issues


def _check_entrypoint_alignment(repo_root: Path) -> list[str]:
    issues: list[str] = []
    architecture = repo_root / "ARCHITECTURE.md"
    pyproject = repo_root / "pyproject.toml"
    setup_py = repo_root / "setup.py"

    for rel, path in (
        ("ARCHITECTURE.md", architecture),
        ("pyproject.toml", pyproject),
        ("setup.py", setup_py),
    ):
        if not path.exists():
            issues.append(f"Missing entrypoint contract file: {rel}")
            return issues

    arch_text = architecture.read_text(encoding="utf-8")
    pyproject_text = pyproject.read_text(encoding="utf-8")
    setup_text = setup_py.read_text(encoding="utf-8")
    commands = sorted(set(re.findall(r"`(ietf-wg-[a-z0-9-]+)`", arch_text)))

    for cmd in commands:
        if cmd not in pyproject_text:
            issues.append(f"Entrypoint missing in pyproject.toml: {cmd}")
        if cmd not in setup_text:
            issues.append(f"Entrypoint missing in setup.py: {cmd}")
    return issues


def _check_module_index_alignment(repo_root: Path) -> list[str]:
    rel = "docs/design-docs/index.md"
    path = repo_root / rel
    if not path.exists():
        return [f"Missing design-doc index: {rel}"]

    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for doc_rel in _module_doc_to_source_relpaths():
        short_rel = doc_rel.replace("docs/design-docs/", "")
        if short_rel not in text:
            issues.append(f"Module doc missing from design-doc index: {short_rel}")
    return issues


def _check_vector_db_schema_contract(repo_root: Path) -> list[str]:
    rel = "docs/generated/db-schema.md"
    path = repo_root / rel
    if not path.exists():
        return [f"Missing vector DB schema doc: {rel}"]

    text = path.read_text(encoding="utf-8")
    required_tokens = [
        '"wg_documents_url_template"',
        '"documents_text"',
        '"documents_fetch_failures"',
        '"deleted_previous"',
    ]

    issues: list[str] = []
    for token in required_tokens:
        if token not in text:
            issues.append(f"Vector DB schema doc missing token: {token}")
    return issues


def run_garbage_collector(root: Optional[Path] = None) -> str:
    """Run deterministic repository hygiene checks for maintainers."""
    repo_root = root or _project_root()

    missing_artifacts: list[str] = []
    for rel in _required_artifact_relpaths():
        if not (repo_root / rel).exists():
            missing_artifacts.append(rel)

    mapping_issues: list[str] = []
    for doc_rel, source_rel in _module_doc_to_source_relpaths().items():
        if not (repo_root / doc_rel).exists():
            mapping_issues.append(f"Missing module doc: {doc_rel}")
        if not (repo_root / source_rel).exists():
            mapping_issues.append(f"Missing source module: {source_rel}")

    skills_issues: list[str] = []
    skills_index = repo_root / "SKILLS.md"
    if skills_index.exists():
        skill_paths = _extract_skill_paths(skills_index.read_text(encoding="utf-8"))
        for rel in skill_paths:
            if not (repo_root / rel).exists():
                skills_issues.append(f"Missing skill doc from registry: {rel}")
    else:
        skills_issues.append("Missing SKILLS.md")

    api_issues: list[str] = []
    api_presence: dict[str, bool] = {}
    ietf_source = repo_root / "src/ietf_wg_agent/ietf.py"
    if ietf_source.exists():
        text = ietf_source.read_text(encoding="utf-8")
        for name in _required_api_contract_names():
            present = bool(re.search(rf"def\s+{re.escape(name)}\s*\(", text))
            api_presence[name] = present
            if not present:
                api_issues.append(f"Missing API contract function: {name}")
    else:
        api_issues.append("Missing src/ietf_wg_agent/ietf.py")
        for name in _required_api_contract_names():
            api_presence[name] = False

    semantic_issues: list[str] = []
    semantic_issues.extend(_check_api_contract_doc_alignment(repo_root, api_presence))
    semantic_issues.extend(_check_entrypoint_alignment(repo_root))
    semantic_issues.extend(_check_module_index_alignment(repo_root))
    semantic_issues.extend(_check_vector_db_schema_contract(repo_root))

    total_issues = (
        len(missing_artifacts)
        + len(mapping_issues)
        + len(skills_issues)
        + len(api_issues)
        + len(semantic_issues)
    )

    lines: list[str] = []
    lines.append("Garbage Collector Report")
    lines.append("------------------------")
    lines.append(
        f"Generated: {datetime.now(timezone.utc).isoformat()}"
    )
    lines.append(f"Repository: {repo_root}")
    lines.append("")

    lines.append("Checks")
    lines.append(f"- Missing required artifacts: {len(missing_artifacts)}")
    lines.append(f"- Module doc/source mapping issues: {len(mapping_issues)}")
    lines.append(f"- Skill registry issues: {len(skills_issues)}")
    lines.append(f"- API contract issues: {len(api_issues)}")
    lines.append(f"- Semantic consistency issues: {len(semantic_issues)}")
    lines.append("")

    if total_issues == 0:
        lines.append("Result: PASS (no inconsistencies found)")
        return "\n".join(lines)

    lines.append("Result: FAIL (inconsistencies found)")
    if missing_artifacts:
        lines.append("")
        lines.append("Missing Artifacts:")
        lines.extend(f"- {item}" for item in missing_artifacts)
    if mapping_issues:
        lines.append("")
        lines.append("Module Mapping Issues:")
        lines.extend(f"- {item}" for item in mapping_issues)
    if skills_issues:
        lines.append("")
        lines.append("Skills Registry Issues:")
        lines.extend(f"- {item}" for item in skills_issues)
    if api_issues:
        lines.append("")
        lines.append("API Contract Issues:")
        lines.extend(f"- {item}" for item in api_issues)
    if semantic_issues:
        lines.append("")
        lines.append("Semantic Consistency Issues:")
        lines.extend(f"- {item}" for item in semantic_issues)

    return "\n".join(lines)


def _format_rebuild(result: RebuildResult) -> str:
    return "\n".join(
        [
            "Rebuilt WG charter DB.",
            f"- Path: {result.db_path}",
            f"- Built at: {result.built_at}",
            f"- WG entries: {result.wg_count}",
            f"- Terms: {result.term_count}",
            f"- Skipped WGs: {result.skipped_wgs}",
            f"- Deleted previous copy: {result.deleted_previous}",
            f"- Checksum: {result.checksum}",
        ]
    )


def _format_metadata(metadata: DbMetadata) -> str:
    if not metadata.exists:
        return "\n".join(
            [
                "WG charter DB metadata",
                f"- Path: {metadata.db_path}",
                "- Exists: False",
            ]
        )

    return "\n".join(
        [
            "WG charter DB metadata",
            f"- Path: {metadata.db_path}",
            "- Exists: True",
            f"- Schema version: {metadata.schema_version}",
            f"- Built at: {metadata.built_at}",
            f"- WG entries: {metadata.wg_count}",
            f"- Terms: {metadata.term_count}",
            f"- Skipped WGs: {metadata.skipped_wgs}",
            f"- Checksum: {metadata.checksum}",
        ]
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Maintainer operations for ietf-wg-agent")
    sub = parser.add_subparsers(dest="command", required=True)

    rebuild = sub.add_parser("rebuild-database", help="Rebuild local WG charter vector DB")
    rebuild.add_argument(
        "--keep-old",
        action="store_true",
        help="Do not delete existing DB file before rebuilding",
    )

    sub.add_parser("db-metadata", help="Show local WG charter DB metadata")

    gc = sub.add_parser(
        "garbage-collector",
        help="Run repo consistency checks for docs, architecture, and API contracts",
    )
    gc.add_argument(
        "--write-report",
        action="store_true",
        help="Write report file under reports/ directory",
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "rebuild-database":
            result = rebuild_wg_charter_db(force_delete_old=not args.keep_old)
            print(_format_rebuild(result))
            return 0

        if args.command == "db-metadata":
            metadata = get_db_metadata()
            print(_format_metadata(metadata))
            return 0

        if args.command == "garbage-collector":
            report = run_garbage_collector()
            print(report)
            if args.write_report:
                out_dir = _project_root() / "reports"
                out_dir.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now(timezone.utc).date().isoformat()
                path = out_dir / f"garbage-collector-{stamp}.txt"
                path.write_text(report + "\n", encoding="utf-8")
                print(f"\nSaved: {path}")
            return 0

        parser.print_help()
        return 2
    except DatatrackerError as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
