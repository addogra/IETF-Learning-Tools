from ietf_wg_agent import ietf


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("http error")


def test_fetch_updates_from_last_two_meetings(monkeypatch):
    html = """
    <html><body>
      <h3>IETF 121</h3>
      <div>
        <a href="/meeting/121/materials/agenda-wg-lsr">Agenda</a>
        <a href="/meeting/121/materials/minutes-wg-lsr">Minutes</a>
      </div>
      <h3>Interim 2026</h3>
      <div>
        <a href="/arch/msg/lsr/interim-note">Agenda</a>
        <a href="/arch/msg/lsr/interim-minutes">Minutes</a>
      </div>
      <h3>IETF 122</h3>
      <div>
        <a href="/meeting/122/materials/agenda-wg-lsr">Agenda</a>
        <a href="/meeting/122/materials/minutes-wg-lsr">Minutes</a>
      </div>
      <h3>IETF 120</h3>
      <div>
        <a href="/meeting/120/materials/agenda-wg-lsr">Agenda</a>
      </div>
    </body></html>
    """

    def fake_get(url, timeout=20):
        assert url.endswith("/wg/lsr/meetings/")
        return _FakeResponse(html)

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    updates = ietf.fetch_updates_from_last_two_meetings("lsr", limit=2)
    assert len(updates) == 2
    assert updates[0].meeting == "IETF 122"
    assert updates[1].meeting == "IETF 121"
    assert updates[0].agendas[0].endswith("agenda-wg-lsr")
    assert updates[0].minutes[0].endswith("minutes-wg-lsr")
    assert all(update.meeting.startswith("IETF ") for update in updates)


def test_fetch_updates_from_last_two_meetings_includes_full_material_text(
    monkeypatch,
):
    meetings_html = """
    <html><body>
      <h3>IETF 122</h3>
      <div>
        <a href="/meeting/122/materials/agenda-wg-lsr">Agenda</a>
        <a href="/meeting/122/materials/minutes-wg-lsr">Minutes</a>
      </div>
    </body></html>
    """
    agenda_html = """
    <html><body>
      <h1>Agenda</h1>
      <p>Item 1: WG status updates</p>
      <p>Item 2: Draft deep dive</p>
      <p>Item 3: Open mic</p>
    </body></html>
    """
    minutes_html = """
    <html><body>
      <h1>Minutes</h1>
      <p>Discussed milestones and dependencies.</p>
      <p>Reviewed draft adoption timeline.</p>
      <p>Recorded follow-up actions.</p>
    </body></html>
    """

    def fake_get(url, timeout=20):
        if url.endswith("/wg/lsr/meetings/"):
            return _FakeResponse(meetings_html)
        if url.endswith("/meeting/122/materials/agenda-wg-lsr"):
            return _FakeResponse(agenda_html)
        if url.endswith("/meeting/122/materials/minutes-wg-lsr"):
            return _FakeResponse(minutes_html)
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    updates = ietf.fetch_updates_from_last_two_meetings(
        "lsr",
        limit=2,
        include_material_text=True,
    )

    assert len(updates) == 1
    assert updates[0].meeting == "IETF 122"
    assert len(updates[0].agenda_details) == 1
    assert len(updates[0].minutes_details) == 1
    assert "Item 1: WG status updates" in updates[0].agenda_details[0].text
    assert "Recorded follow-up actions." in updates[0].minutes_details[0].text
