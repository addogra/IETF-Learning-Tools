# Author: Aditya Dogra
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
      <h3>IETF 122</h3>
      <div>
        <a href="/meeting/122/materials/agenda-wg-lsr">Agenda</a>
        <a href="/meeting/122/materials/minutes-wg-lsr">Minutes</a>
      </div>
      <h3>IETF 121</h3>
      <div>
        <a href="/meeting/121/materials/agenda-wg-lsr">Agenda</a>
        <a href="/meeting/121/materials/minutes-wg-lsr">Minutes</a>
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
