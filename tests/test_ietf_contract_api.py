from datetime import datetime, timedelta, timezone

from ietf_wg_agent import ietf
from ietf_wg_agent.ietf import (
    CharterResult,
    DiscussionPost,
    DiscussionSummary,
    LastMeetingItem,
    MeetingUpdate,
    SubscriptionConfig,
    UpcomingAgendaItem,
    WorkingGroup,
)
from ietf_wg_agent.subscriptions import Subscription


def _mock_resolve(monkeypatch, wg: WorkingGroup) -> None:
    monkeypatch.setattr(ietf, "fetch_working_groups", lambda timeout=20: [wg])
    monkeypatch.setattr(ietf, "resolve_working_group", lambda _q, _groups: wg)


def test_get_wg_charter_wrapper(monkeypatch):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")
    _mock_resolve(monkeypatch, wg)
    monkeypatch.setattr(ietf, "fetch_charter_text", lambda _ac: "full charter")

    result = ietf.get_wg_charter("LSR")

    assert isinstance(result, CharterResult)
    assert result.wg_id == "lsr"
    assert result.wg_name == "Link State Routing"
    assert result.charter_text == "full charter"
    assert result.source_url.endswith("/wg/lsr/about/")


def test_get_wg_active_drafts_wrapper(monkeypatch):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")
    _mock_resolve(monkeypatch, wg)
    monkeypatch.setattr(
        ietf,
        "fetch_top_active_drafts",
        lambda _ac, limit=5: [
            ietf.DraftInfo(
                name="draft-ietf-lsr-example-00",
                title="Example Title",
                status="WG Document",
                abstract="Example abstract",
                url="https://datatracker.ietf.org/doc/draft-ietf-lsr-example-00/",
            )
        ],
    )

    drafts = ietf.get_wg_active_drafts("lsr", limit=5)

    assert len(drafts) == 1
    assert drafts[0].identifier == "draft-ietf-lsr-example-00"
    assert drafts[0].title == "Example Title"


def test_get_wg_discussion_summary_wrapper_filters_window(monkeypatch):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")
    _mock_resolve(monkeypatch, wg)

    now = datetime.now(timezone.utc)
    new_post = DiscussionPost(
        date=now.isoformat(),
        subject="New thread",
        author="Alice",
        url="https://mailarchive.ietf.org/arch/msg/lsr/new/",
    )
    old_post = DiscussionPost(
        date=(now - timedelta(days=5)).isoformat(),
        subject="Old thread",
        author="Bob",
        url="https://mailarchive.ietf.org/arch/msg/lsr/old/",
    )
    monkeypatch.setattr(
        ietf,
        "fetch_wg_discussions_last_months",
        lambda _ac, months=1: [new_post, old_post],
    )

    summary = ietf.get_wg_discussion_summary("lsr", window_days=1)

    assert summary.post_count == 1
    assert summary.posts[0].subject == "New thread"
    assert "last 1 days" in summary.summary


def test_get_wg_last_two_meeting_updates_wrapper(monkeypatch):
    wg = WorkingGroup(acronym="lsr", name="Link State Routing")
    _mock_resolve(monkeypatch, wg)
    monkeypatch.setattr(
        ietf,
        "fetch_updates_from_last_two_meetings",
        lambda _ac, limit=2: [
            MeetingUpdate(
                meeting="IETF 122",
                agendas=["https://datatracker.ietf.org/meeting/122/materials/agenda-lsr"],
                minutes=["https://datatracker.ietf.org/meeting/122/materials/minutes-lsr"],
            )
        ],
    )

    result = ietf.get_wg_last_two_meeting_updates("lsr")

    assert result.wg_id == "lsr"
    assert len(result.updates) == 1
    assert result.source_url.endswith("/wg/lsr/meetings/")


def test_get_upcoming_and_last_meeting_summary_wrappers(monkeypatch):
    groups = [WorkingGroup(acronym="lsr", name="Link State Routing")]
    monkeypatch.setattr(ietf, "fetch_working_groups", lambda timeout=20: groups)
    monkeypatch.setattr(
        ietf,
        "fetch_upcoming_ietf_agenda",
        lambda _groups: (
            "IETF 122 - March 1, 2027 - March 7, 2027 - Yokohama, Japan",
            [
                UpcomingAgendaItem(
                    wg_acronym="lsr",
                    wg_name="Link State Routing",
                    agenda_url="https://datatracker.ietf.org/meeting/122/materials/agenda-lsr",
                    agenda_summary="Agenda summary",
                )
            ],
        ),
    )
    monkeypatch.setattr(
        ietf,
        "fetch_summary_of_last_ietf_meeting",
        lambda _groups: (
            "IETF 121 - November 1, 2026 - November 7, 2026 - Madrid, Spain",
            [
                LastMeetingItem(
                    wg_acronym="lsr",
                    wg_name="Link State Routing",
                    agenda_url="https://datatracker.ietf.org/meeting/121/materials/agenda-lsr",
                    minutes_url="https://datatracker.ietf.org/meeting/121/materials/minutes-lsr",
                    minutes_summary="Minutes summary",
                )
            ],
        ),
    )

    upcoming = ietf.get_upcoming_ietf_agenda_summary()
    last = ietf.get_last_ietf_meeting_summary()

    assert "IETF 122" in upcoming.header
    assert len(upcoming.items) == 1
    assert "IETF 121" in last.header
    assert len(last.items) == 1


def test_track_draft_or_rfc_not_found(monkeypatch):
    class _Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"objects": []}

    monkeypatch.setattr(ietf.requests, "get", lambda *args, **kwargs: _Response())

    result = ietf.track_draft_or_rfc("rfc999999")

    assert result.found is False
    assert result.canonical_identifier == "rfc999999"
    assert "No Datatracker document found" in result.message


def test_run_daily_wg_update_notifies_subscribers(monkeypatch):
    monkeypatch.setattr(
        ietf,
        "get_wg_discussion_summary",
        lambda wg_id, window_days=1: DiscussionSummary(
            wg_id="lsr",
            wg_name="Link State Routing",
            window_days=1,
            post_count=1,
            summary="Draft discussions summary (last 1 day):",
            posts=[],
        ),
    )
    monkeypatch.setattr(
        "ietf_wg_agent.subscriptions.list_subscriptions",
        lambda: [
            Subscription(user_id="alice@example.com", acronym="lsr"),
            Subscription(user_id="bob", acronym="lsr"),
            Subscription(user_id="charlie@example.com", acronym="bess"),
        ],
    )
    monkeypatch.setattr("ietf_wg_agent.notifier.load_smtp_config", lambda: object())

    sent: list[str] = []

    def _fake_send_email(to_email: str, subject: str, body: str, config):
        sent.append(to_email)

    monkeypatch.setattr("ietf_wg_agent.notifier.send_email", _fake_send_email)

    result = ietf.run_daily_wg_update("lsr", notify=True)

    assert result.post_count == 1
    assert result.notified_recipients == 1
    assert sent == ["alice@example.com"]
    assert result.notification_errors == []


def test_schedule_daily_updates_registers_and_starts_scheduler(monkeypatch):
    monkeypatch.setattr(
        ietf,
        "_resolve_wg_or_raise",
        lambda _wg_id: WorkingGroup(acronym="lsr", name="Link State Routing"),
    )

    calls: list[tuple[str, str]] = []

    def _fake_register(user_id: str, acronym: str):
        calls.append((user_id, acronym))

    monkeypatch.setattr("ietf_wg_agent.subscriptions.register_daily_update", _fake_register)
    monkeypatch.setattr(
        ietf,
        "_start_daily_updates_scheduler",
        lambda interval_hours=24: (
            True,
            "ietf-wg-daily-updates-scheduler",
            "Scheduler started (pid=1234).",
        ),
    )

    result = ietf.schedule_daily_updates(
        SubscriptionConfig(
            user_id="alice@example.com",
            wg_id="lsr",
            start_scheduler=True,
            interval_hours=12,
        )
    )

    assert calls == [("alice@example.com", "lsr")]
    assert result.registered is True
    assert result.scheduler_started is True
    assert "Scheduler started" in result.message
