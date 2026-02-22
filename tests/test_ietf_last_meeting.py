# Author: Aditya Dogra
from ietf_wg_agent import ietf


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("http error")


def test_fetch_summary_of_last_ietf_meeting(monkeypatch):
    index_html = """
    <html><body>
      <a href="/meeting/122/">IETF 122</a>
      <a href="/meeting/121/">IETF 121</a>
    </body></html>
    """
    # 122 is future; 121 is completed.
    mtg_122_html = """
    <html><body><p>December 01, 2099 - December 05, 2099</p><p>Location: Future City</p></body></html>
    """
    mtg_121_html = """
    <html><body><p>March 15, 2024 - March 21, 2024</p><p>Location: Brisbane, Australia</p></body></html>
    """

    lsr_meetings = """
    <html><body>
      <h3>IETF 121</h3>
      <a href="/meeting/121/materials/agenda-lsr">Agenda</a>
      <a href="/meeting/121/materials/minutes-lsr">Minutes</a>
    </body></html>
    """
    idr_meetings = """
    <html><body>
      <h3>IETF 121</h3>
      <a href="/meeting/121/materials/agenda-idr">Agenda</a>
    </body></html>
    """
    minutes_lsr_html = """
    <html><body><h2>Minutes</h2><p>Reviewed milestones and progressed two drafts.</p></body></html>
    """

    def fake_get(url, timeout=20):
        if url == ietf.MEETINGS_INDEX_URL:
            return _FakeResponse(index_html)
        if url == ietf.MEETING_PAGE_URL_TEMPLATE.format(number="122"):
            return _FakeResponse(mtg_122_html)
        if url == ietf.MEETING_PAGE_URL_TEMPLATE.format(number="121"):
            return _FakeResponse(mtg_121_html)
        if url.endswith("/wg/lsr/meetings/"):
            return _FakeResponse(lsr_meetings)
        if url.endswith("/wg/idr/meetings/"):
            return _FakeResponse(idr_meetings)
        if url.endswith("/meeting/121/materials/minutes-lsr"):
            return _FakeResponse(minutes_lsr_html)
        if url.endswith("/meeting/121/materials/agenda-lsr"):
            return _FakeResponse("<html><body>Agenda</body></html>")
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    groups = [
        ietf.WorkingGroup(acronym="lsr", name="Link State Routing"),
        ietf.WorkingGroup(acronym="idr", name="Inter-Domain Routing"),
    ]

    header, items = ietf.fetch_summary_of_last_ietf_meeting(groups)
    assert header.startswith("IETF 121")
    assert "Brisbane" in header
    assert len(items) == 1
    assert items[0].wg_acronym.lower() == "lsr"
    assert "Reviewed milestones" in items[0].minutes_summary
