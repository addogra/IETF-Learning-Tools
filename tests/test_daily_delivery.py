# Author: Aditya Dogra
from types import SimpleNamespace

from ietf_wg_agent import daily
from ietf_wg_agent.ietf import LastMeetingItem, MeetingUpdate, UpcomingAgendaItem


def test_deliver_daily_emails_no_subscriptions(monkeypatch):
    monkeypatch.setattr(daily, "_build_user_reports", lambda: {})
    result = daily.deliver_daily_emails()
    assert result == "No subscriptions found. No emails sent."


def test_deliver_daily_emails_delivered_skipped_and_failed(monkeypatch):
    reports = {
        "ok@example.com": "body-ok",
        "not-an-email": "body-skip",
        "fail@example.com": "body-fail",
    }

    monkeypatch.setattr(daily, "_build_user_reports", lambda: reports)
    monkeypatch.setattr(
        daily,
        "load_smtp_config",
        lambda: SimpleNamespace(retries=3, backoff_seconds=1.5, jitter_seconds=0.5),
    )

    sent = []

    def fake_send_email(to_email: str, subject: str, body: str, config):
        if to_email == "fail@example.com":
            raise RuntimeError("smtp rejected")
        sent.append((to_email, body))

    monkeypatch.setattr(daily, "send_email", fake_send_email)

    result = daily.deliver_daily_emails()

    assert ("ok@example.com", "body-ok") in sent
    assert "Emails delivered: 1" in result
    assert "Delivery settings: retries=3, backoff_seconds=1.5, jitter_seconds=0.5" in result
    assert "- not-an-email" in result
    assert "fail@example.com (send failed: smtp rejected)" in result


def test_build_user_reports_includes_meeting_updates(monkeypatch):
    monkeypatch.setattr(
        daily,
        "list_subscriptions",
        lambda: [SimpleNamespace(user_id="u@example.com", acronym="lsr")],
    )
    monkeypatch.setattr(daily, "fetch_charter_text", lambda _ac: "charter text")
    monkeypatch.setattr(daily, "summarize_charter", lambda _txt: "charter summary")
    monkeypatch.setattr(
        daily,
        "fetch_working_groups",
        lambda: [SimpleNamespace(acronym="lsr", name="Link State Routing")],
    )
    monkeypatch.setattr(
        daily,
        "fetch_upcoming_ietf_agenda",
        lambda _groups: (
            "IETF 122 - March 15, 2027 - March 21, 2027 - Yokohama, Japan",
            [
                UpcomingAgendaItem(
                    wg_acronym="lsr",
                    wg_name="Link State Routing",
                    agenda_url="https://datatracker.ietf.org/meeting/122/materials/agenda-lsr",
                    agenda_summary="Agenda summary text.",
                )
            ],
        ),
    )
    monkeypatch.setattr(
        daily,
        "fetch_summary_of_last_ietf_meeting",
        lambda _groups: (
            "IETF 121 - March 15, 2024 - March 21, 2024 - Brisbane, Australia",
            [
                LastMeetingItem(
                    wg_acronym="lsr",
                    wg_name="Link State Routing",
                    agenda_url="https://datatracker.ietf.org/meeting/121/materials/agenda-lsr",
                    minutes_url="https://datatracker.ietf.org/meeting/121/materials/minutes-lsr",
                    minutes_summary="Reviewed milestones and progressed two drafts.",
                )
            ],
        ),
    )
    monkeypatch.setattr(
        daily,
        "fetch_updates_from_last_two_meetings",
        lambda _ac, limit=2: [
            MeetingUpdate(
                meeting="IETF 122",
                agendas=["https://datatracker.ietf.org/meeting/122/materials/agenda-wg-lsr"],
                minutes=["https://datatracker.ietf.org/meeting/122/materials/minutes-wg-lsr"],
            )
        ],
    )

    reports = daily._build_user_reports()
    body = reports["u@example.com"]
    assert "charter summary" in body
    assert "Updates from last 2 IETF meetings:" in body
    assert "IETF 122" in body
    assert "Working Group Link State Routing (LSR)" in body
    assert "IETF 121" in body
    assert "Reviewed milestones and progressed two drafts." in body


def test_deliver_daily_discussion_updates_emails_only_when_updates(monkeypatch):
    monkeypatch.setattr(
        daily,
        "_build_user_discussion_reports",
        lambda days=1: {
            "ok@example.com": "discussion-body",
        },
    )
    monkeypatch.setattr(
        daily,
        "load_smtp_config",
        lambda: SimpleNamespace(retries=3, backoff_seconds=1.5, jitter_seconds=0.5),
    )
    sent = []

    def fake_send_email(to_email: str, subject: str, body: str, config):
        sent.append((to_email, body))

    monkeypatch.setattr(daily, "send_email", fake_send_email)
    result = daily.deliver_daily_discussion_updates_emails(days=1)
    assert ("ok@example.com", "discussion-body") in sent
    assert "Discussion update emails delivered: 1" in result


def test_deliver_daily_discussion_updates_emails_no_updates(monkeypatch):
    monkeypatch.setattr(daily, "_build_user_discussion_reports", lambda days=1: {})
    result = daily.deliver_daily_discussion_updates_emails(days=1)
    assert result == "No discussion updates in the last 1 day. No emails sent."
