# Author: Aditya Dogra
from ietf_wg_agent import ietf


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("http error")


def test_fetch_upcoming_ietf_agenda(monkeypatch):
    index_html = """
    <html><body>
      <a href="/meeting/121/">IETF 121</a>
      <a href="/meeting/122/">IETF 122</a>
    </body></html>
    """
    meeting_page_html = """
    <html><body>
      <h1>IETF 122</h1>
      <p>March 15, 2027 - March 21, 2027</p>
      <p>Location: Yokohama, Japan</p>
    </body></html>
    """
    lsr_meetings_html = """
    <html><body>
      <h3>IETF 122</h3>
      <a href="/meeting/122/materials/agenda-lsr">Agenda</a>
    </body></html>
    """
    bess_meetings_html = """
    <html><body>
      <h3>IETF 122</h3>
      <a href="/meeting/122/materials/agenda-bess">Agenda</a>
    </body></html>
    """
    idr_meetings_html = """
    <html><body>
      <h3>IETF 122</h3>
      <p>No agenda yet</p>
    </body></html>
    """
    agenda_lsr_html = """
    <html><body><h2>Agenda</h2><p>Review LSR milestones and draft status updates.</p></body></html>
    """
    agenda_bess_html = """
    <html><body><h2>Agenda</h2><p>Discuss BESS EVPN implementation reports and next steps.</p></body></html>
    """

    def fake_get(url, timeout=20):
        if url == ietf.MEETINGS_INDEX_URL:
            return _FakeResponse(index_html)
        if url == ietf.MEETING_PAGE_URL_TEMPLATE.format(number="122"):
            return _FakeResponse(meeting_page_html)
        if url.endswith("/wg/lsr/meetings/"):
            return _FakeResponse(lsr_meetings_html)
        if url.endswith("/wg/bess/meetings/"):
            return _FakeResponse(bess_meetings_html)
        if url.endswith("/wg/idr/meetings/"):
            return _FakeResponse(idr_meetings_html)
        if url.endswith("/meeting/122/materials/agenda-lsr"):
            return _FakeResponse(agenda_lsr_html)
        if url.endswith("/meeting/122/materials/agenda-bess"):
            return _FakeResponse(agenda_bess_html)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    groups = [
        ietf.WorkingGroup(acronym="lsr", name="Link State Routing"),
        ietf.WorkingGroup(acronym="bess", name="BGP Enabled ServiceS"),
        ietf.WorkingGroup(acronym="idr", name="Inter-Domain Routing"),
    ]

    header, items = ietf.fetch_upcoming_ietf_agenda(groups)
    assert header.startswith("IETF 122")
    assert "March" in header
    assert "Yokohama" in header
    assert len(items) == 2
    assert {i.wg_acronym.lower() for i in items} == {"lsr", "bess"}
    assert all(i.agenda_summary for i in items)
