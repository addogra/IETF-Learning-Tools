from ietf_wg_agent import maintainer
from ietf_wg_agent.ietf import RebuildResult


def test_maintainer_rebuild_command_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(
        maintainer,
        "rebuild_wg_charter_db",
        lambda force_delete_old=True: RebuildResult(
            db_path="/tmp/wg_charter_vector_db.json",
            built_at="2026-02-28T00:00:00+00:00",
            wg_count=10,
            term_count=123,
            skipped_wgs=2,
            deleted_previous=force_delete_old,
            checksum="abc123",
        ),
    )

    rc = maintainer.main(["rebuild-database"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Rebuilt WG charter DB." in out
    assert "WG entries: 10" in out


def test_run_garbage_collector_reports_missing_api(monkeypatch, tmp_path):
    src = tmp_path / "src" / "ietf_wg_agent"
    src.mkdir(parents=True)
    (src / "ietf.py").write_text("def api_a():\n    return None\n", encoding="utf-8")

    monkeypatch.setattr(maintainer, "_required_artifact_relpaths", lambda: [])
    monkeypatch.setattr(maintainer, "_module_doc_to_source_relpaths", lambda: {})
    monkeypatch.setattr(maintainer, "_required_api_contract_names", lambda: ["api_a", "api_b"])
    monkeypatch.setattr(
        maintainer,
        "_check_api_contract_doc_alignment",
        lambda _root, _presence: [],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_entrypoint_alignment",
        lambda _root: [],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_module_index_alignment",
        lambda _root: [],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_vector_db_schema_contract",
        lambda _root: [],
    )

    report = maintainer.run_garbage_collector(root=tmp_path)
    assert "Missing API contract function: api_b" in report


def test_run_garbage_collector_passes_on_empty_requirements(monkeypatch, tmp_path):
    monkeypatch.setattr(maintainer, "_required_artifact_relpaths", lambda: [])
    monkeypatch.setattr(maintainer, "_module_doc_to_source_relpaths", lambda: {})
    monkeypatch.setattr(maintainer, "_required_api_contract_names", lambda: [])
    monkeypatch.setattr(
        maintainer,
        "_check_api_contract_doc_alignment",
        lambda _root, _presence: [],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_entrypoint_alignment",
        lambda _root: [],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_module_index_alignment",
        lambda _root: [],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_vector_db_schema_contract",
        lambda _root: [],
    )

    src = tmp_path / "src" / "ietf_wg_agent"
    src.mkdir(parents=True)
    (src / "ietf.py").write_text("", encoding="utf-8")
    (tmp_path / "SKILLS.md").write_text("", encoding="utf-8")
    report = maintainer.run_garbage_collector(root=tmp_path)
    assert "Result: PASS" in report


def test_run_garbage_collector_reports_semantic_issues(monkeypatch, tmp_path):
    src = tmp_path / "src" / "ietf_wg_agent"
    src.mkdir(parents=True)
    (src / "ietf.py").write_text("def api_a():\n    return None\n", encoding="utf-8")

    monkeypatch.setattr(maintainer, "_required_artifact_relpaths", lambda: [])
    monkeypatch.setattr(maintainer, "_module_doc_to_source_relpaths", lambda: {})
    monkeypatch.setattr(maintainer, "_required_api_contract_names", lambda: ["api_a"])
    monkeypatch.setattr(
        maintainer,
        "_check_api_contract_doc_alignment",
        lambda _root, _presence: ["doc mismatch"],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_entrypoint_alignment",
        lambda _root: [],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_module_index_alignment",
        lambda _root: [],
    )
    monkeypatch.setattr(
        maintainer,
        "_check_vector_db_schema_contract",
        lambda _root: [],
    )

    report = maintainer.run_garbage_collector(root=tmp_path)
    assert "Semantic consistency issues: 1" in report
    assert "doc mismatch" in report
