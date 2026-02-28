from ietf_wg_agent import discussion_scheduler as sched


def test_scheduler_run_once(monkeypatch):
    monkeypatch.setattr(
        sched,
        "deliver_daily_discussion_updates_emails",
        lambda days=1: "Discussion update emails delivered: 1",
    )
    assert sched.run_once() == "Discussion update emails delivered: 1"
