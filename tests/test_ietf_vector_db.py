import json

import pytest

from ietf_wg_agent import ietf
from ietf_wg_agent.ietf import WorkingGroup


def test_rebuild_wg_charter_db_and_metadata(monkeypatch, tmp_path):
    db_path = tmp_path / "wg_charter_vector_db.json"

    groups = [
        WorkingGroup(acronym="lsr", name="Link State Routing"),
        WorkingGroup(acronym="sidrops", name="SIDR Operations"),
    ]
    charters = {
        "lsr": "The working group focuses on OSPF security and link-state routing.",
        "sidrops": "The group focuses on routing security, RPKI, and operations.",
    }

    monkeypatch.setattr(ietf, "_charter_db_path", lambda: db_path)
    monkeypatch.setattr(ietf, "crawl_active_working_groups", lambda timeout=20: groups)
    monkeypatch.setattr(ietf, "fetch_charter_text", lambda acronym: charters[acronym])
    monkeypatch.setattr(
        ietf,
        "fetch_wg_documents_section_text",
        lambda acronym: f"Documents section for {acronym}",
    )

    result = ietf.rebuild_wg_charter_db()
    metadata = ietf.get_db_metadata()

    assert result.wg_count == 2
    assert result.term_count > 0
    assert result.deleted_previous is False
    assert metadata.exists is True
    assert metadata.wg_count == 2
    assert metadata.term_count == result.term_count
    assert db_path.exists()

    payload = json.loads(db_path.read_text(encoding="utf-8"))
    assert payload["stats"]["wg_count"] == 2
    assert payload["schema_version"] == 1
    assert payload["documents"][0]["charter_text"]


def test_rebuild_wg_charter_db_deletes_previous_copy(monkeypatch, tmp_path):
    db_path = tmp_path / "wg_charter_vector_db.json"
    db_path.write_text('{"old": true}', encoding="utf-8")

    groups = [WorkingGroup(acronym="lsr", name="Link State Routing")]
    monkeypatch.setattr(ietf, "_charter_db_path", lambda: db_path)
    monkeypatch.setattr(ietf, "crawl_active_working_groups", lambda timeout=20: groups)
    monkeypatch.setattr(
        ietf,
        "fetch_charter_text",
        lambda acronym: "OSPF extensions and security work in this charter.",
    )
    monkeypatch.setattr(
        ietf,
        "fetch_wg_documents_section_text",
        lambda acronym: "Documents section text",
    )

    result = ietf.rebuild_wg_charter_db(force_delete_old=True)
    assert result.deleted_previous is True


def test_suggest_wgs_by_technology_and_semantics(monkeypatch, tmp_path):
    db_path = tmp_path / "wg_charter_vector_db.json"
    groups = [
        WorkingGroup(acronym="lsr", name="Link State Routing"),
        WorkingGroup(acronym="bess", name="BGP Enabled ServiceS"),
    ]
    charters = {
        "lsr": "The WG works on OSPF security and link-state extensions.",
        "bess": "The WG works on BGP services and EVPN extensions.",
    }

    monkeypatch.setattr(ietf, "_charter_db_path", lambda: db_path)
    monkeypatch.setattr(ietf, "crawl_active_working_groups", lambda timeout=20: groups)
    monkeypatch.setattr(ietf, "fetch_charter_text", lambda acronym: charters[acronym])
    monkeypatch.setattr(
        ietf,
        "fetch_wg_documents_section_text",
        lambda acronym: f"Documents section for {acronym}",
    )
    ietf.rebuild_wg_charter_db()

    matches = ietf.suggest_wgs_by_technology("OSPF security", top_k=5, require_all_terms=True)
    assert matches
    assert matches[0].acronym == "LSR"
    assert "Matched terms:" in matches[0].justification

    no_match = ietf.suggest_wgs_by_technology(
        "OSPF EVPN", top_k=5, require_all_terms=True
    )
    assert no_match == []


def test_suggest_wgs_by_technology_raises_when_db_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(ietf, "_charter_db_path", lambda: tmp_path / "missing.json")
    with pytest.raises(ietf.DatatrackerError):
        ietf.suggest_wgs_by_technology("ospf security")


def test_resolve_wg_name_wrapper(monkeypatch):
    groups = [
        WorkingGroup(acronym="lsr", name="Link State Routing"),
        WorkingGroup(acronym="bess", name="BGP Enabled ServiceS"),
    ]
    monkeypatch.setattr(ietf, "fetch_working_groups", lambda timeout=20: groups)

    result = ietf.resolve_wg_name("LSR")
    assert result.matched is not None
    assert result.matched.acronym == "lsr"
    assert result.suggestions == []


def test_documents_section_terms_are_included_in_vector_db(monkeypatch, tmp_path):
    db_path = tmp_path / "wg_charter_vector_db.json"
    groups = [WorkingGroup(acronym="rtgwg", name="Routing Area Working Group")]

    monkeypatch.setattr(ietf, "_charter_db_path", lambda: db_path)
    monkeypatch.setattr(ietf, "crawl_active_working_groups", lambda timeout=20: groups)
    monkeypatch.setattr(
        ietf,
        "fetch_charter_text",
        lambda acronym: "General routing-area intake and process charter text.",
    )
    monkeypatch.setattr(
        ietf,
        "fetch_wg_documents_section_text",
        lambda acronym: "draft-ietf-rtgwg-vrrp-bfd and related VRRP BFD tracking",
    )

    ietf.rebuild_wg_charter_db()

    strict = ietf.suggest_wgs_by_technology(
        "vrrp bfd", top_k=5, require_all_terms=True
    )
    assert strict
    assert strict[0].acronym == "RTGWG"
