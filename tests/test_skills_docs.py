# Author: Aditya Dogra
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SECTIONS = [
    "## Purpose",
    "## Inputs",
    "## Steps",
    "## Outputs",
    "## Failure Handling",
    "## Test Coverage",
]


def _parse_registry_rows(text: str):
    rows = []
    for line in text.splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", line)
        if m:
            rows.append((m.group(1), m.group(2)))
    return rows


def test_skills_registry_exists_and_has_rows():
    skills_index = ROOT / "SKILLS.md"
    assert skills_index.exists(), "SKILLS.md missing"
    rows = _parse_registry_rows(skills_index.read_text(encoding="utf-8"))
    assert rows, "No skill registry rows found in SKILLS.md"


def test_all_registry_paths_exist_and_are_skill_docs():
    skills_index = ROOT / "SKILLS.md"
    rows = _parse_registry_rows(skills_index.read_text(encoding="utf-8"))

    for skill_name, rel_path in rows:
        path = ROOT / rel_path
        assert path.exists(), f"Skill path missing for {skill_name}: {rel_path}"
        assert path.name == "SKILL.md", f"Invalid skill doc filename for {skill_name}"


def test_each_skill_has_required_sections():
    skills_index = ROOT / "SKILLS.md"
    rows = _parse_registry_rows(skills_index.read_text(encoding="utf-8"))

    for skill_name, rel_path in rows:
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            assert section in text, f"{skill_name} missing section: {section}"
