from ietf_wg_agent.ietf import WorkingGroup, suggest_working_groups


def test_suggest_working_groups_for_acronym_typo():
    groups = [
        WorkingGroup(acronym="LSR", name="Link State Routing"),
        WorkingGroup(acronym="LSVR", name="Link State Vector Routing"),
        WorkingGroup(acronym="IDR", name="Inter-Domain Routing"),
        WorkingGroup(acronym="BESS", name="BGP Enabled Services"),
    ]

    result = suggest_working_groups("LSRV", groups, limit=3)
    acronyms = [wg.acronym for wg in result]

    assert "LSVR" in acronyms
    assert "LSR" in acronyms
    assert "IDR" not in acronyms
    assert "BESS" not in acronyms


def test_suggest_working_groups_for_name_keywords():
    groups = [
        WorkingGroup(acronym="LSR", name="Link State Routing"),
        WorkingGroup(acronym="LSVR", name="Link State Vector Routing"),
        WorkingGroup(acronym="IDR", name="Inter-Domain Routing"),
    ]

    result = suggest_working_groups("link state", groups, limit=3)
    acronyms = [wg.acronym for wg in result]

    assert "LSR" in acronyms
    assert "LSVR" in acronyms
