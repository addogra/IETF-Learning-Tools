from ietf_wg_agent import ietf


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("http error")


def test_fetch_working_groups_default_timeout_and_error_url(monkeypatch):
    captured: dict[str, int] = {}

    def fake_get(url, params=None, timeout=0):
        captured["timeout"] = timeout
        raise ietf.requests.RequestException("network down")

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    try:
        ietf.fetch_working_groups()
        assert False, "expected DatatrackerError"
    except ietf.DatatrackerError as exc:
        message = str(exc)
        assert "Unable to access URL" in message
        assert ietf.WG_API_URL in message

    assert captured["timeout"] == ietf.HTTP_TIMEOUT_SECONDS


def test_fetch_upcoming_ietf_agenda(monkeypatch):
    important_dates_html = """
    <html><body>
      <h2>IETF 125</h2>
      <p>2026-03-14, Shenzhen, CN</p>
      <table>
        <tr><th>Date</th><th>Weekday</th><th>Description</th></tr>
        <tr><td>2025-09-22</td><td>Mon</td><td>Week of IETF Online Registration Opens (UTC)</td></tr>
        <tr><td>2026-03-09</td><td>Mon</td><td>Final agenda to be published</td></tr>
        <tr><td>2026-03-02</td><td>Mon</td><td>Internet-Draft submission cut-off</td></tr>
        <tr><td>2026-03-16</td><td>Mon</td><td>Registration cancellation cut-off</td></tr>
      </table>
      <h2>IETF 126</h2>
      <p>2026-07-18, Vienna, AT</p>
      <table>
        <tr><th>Date</th><th>Weekday</th><th>Description</th></tr>
        <tr><td>2026-03-30</td><td>Mon</td><td>Week of IETF Online Registration Opens (UTC)</td></tr>
        <tr><td>2026-06-19</td><td>Fri</td><td>Preliminary Agenda published</td></tr>
        <tr><td>2026-07-06</td><td>Mon</td><td>Internet-Draft submission cut-off</td></tr>
        <tr><td>2026-07-13</td><td>Mon</td><td>Registration cancellation cut-off</td></tr>
      </table>
      <h2>IETF 127</h2>
      <p>2026-11-14, San Francisco, US</p>
      <table>
        <tr><th>Date</th><th>Weekday</th><th>Description</th></tr>
        <tr><td>2026-07-27</td><td>Mon</td><td>Week of IETF Online Registration Opens (UTC)</td></tr>
        <tr><td>2026-10-16</td><td>Fri</td><td>Final agenda to be published</td></tr>
        <tr><td>2026-11-02</td><td>Mon</td><td>Internet-Draft submission cut-off</td></tr>
        <tr><td>2026-11-09</td><td>Mon</td><td>Registration cancellation cut-off</td></tr>
      </table>
    </body></html>
    """
    agenda_txt = """
IETF 125 Agenda as of 2026-03-10 10:00:00 UTC
0900-1100 Mon Morning Session I lsr Link State Routing WG updates
1130-1230 Mon Morning Session II bess BGP Enabled ServiceS status review
"""

    def fake_get(url, timeout=20):
        if url == ietf.IMPORTANT_DATES_URL:
            return _FakeResponse(important_dates_html)
        if url == ietf.MEETING_AGENDA_TXT_URL_TEMPLATE.format(number="125"):
            return _FakeResponse(agenda_txt)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    groups = [
        ietf.WorkingGroup(acronym="lsr", name="Link State Routing"),
        ietf.WorkingGroup(acronym="bess", name="BGP Enabled ServiceS"),
        ietf.WorkingGroup(acronym="idr", name="Inter-Domain Routing"),
    ]

    header, items = ietf.fetch_upcoming_ietf_agenda(groups)
    assert "Next IETF events planned and dates and location:" in header
    assert "IETF 125 - Dates 2026-03-14 - Place Shenzhen, CN" in header
    assert "IETF 126 - Dates 2026-07-18 - Place Vienna, AT" in header
    assert "IETF 127 - Dates 2026-11-14 - Place San Francisco, US" in header
    assert "Important details (IETF 125):" in header
    assert "IETF Online Registration Opens: 2025-09-22" in header
    assert "Final agenda to be published: 2026-03-09" in header
    assert "Agenda link - for IETF-125: https://datatracker.ietf.org/meeting/125/agenda.txt" in header
    assert "Internet-Draft submission cut-off: 2026-03-02" in header
    assert "Registration cancellation cut-off: 2026-03-16" in header
    assert "Important details (IETF 126):" in header
    assert "Final agenda to be published: 2026-06-19" in header
    assert "Important details (IETF 127):" in header
    assert items == []


def test_fetch_upcoming_ietf_agenda_not_published_notice(monkeypatch):
    important_dates_html = """
    <html><body>
      <h2>IETF 126</h2>
      <p>2099-07-18, Vienna, AT</p>
      <table>
        <tr><th>Date</th><th>Weekday</th><th>Description</th></tr>
        <tr><td>2099-03-01</td><td>Mon</td><td>Week of IETF Online Registration Opens (UTC)</td></tr>
        <tr><td>2099-06-19</td><td>Mon</td><td>Preliminary Agenda published</td></tr>
        <tr><td>2099-07-06</td><td>Mon</td><td>Internet-Draft submission cut-off</td></tr>
        <tr><td>2099-07-10</td><td>Mon</td><td>Registration cancellation cut-off</td></tr>
      </table>
    </body></html>
    """
    agenda_txt = """
IETF 126 Agenda as of 2099-05-01 10:00:00 UTC
"""

    def fake_get(url, timeout=20):
        if url == ietf.IMPORTANT_DATES_URL:
            return _FakeResponse(important_dates_html)
        if url == ietf.MEETING_AGENDA_TXT_URL_TEMPLATE.format(number="126"):
            return _FakeResponse(agenda_txt)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    groups = [
        ietf.WorkingGroup(acronym="lsr", name="Link State Routing"),
        ietf.WorkingGroup(acronym="bess", name="BGP Enabled ServiceS"),
    ]

    header, items = ietf.fetch_upcoming_ietf_agenda(groups)
    assert "Final agenda to be published: 2099-06-19" in header
    assert (
        "Agenda is NOT yet published, for this IETF-126,"
        "Final agenda will be published on 2099-06-19."
    ) in header
    assert items == []


def test_parse_upcoming_events_prefers_heading_small_for_place():
    html = """
    <html><body>
      <h2 class="mt-5" id="IETF127">
        IETF 127
        <small class="text-body-secondary">2026-11-14, San Francisco, US</small>
      </h2>
      <table>
        <tr><th>Date</th><th>Weekday</th><th>Description</th></tr>
        <tr><td>2026-08-17</td><td>Monday</td><td>Week of IETF Online Registration Opens (UTC)</td></tr>
        <tr><td>2026-10-16</td><td>Friday</td><td>Final agenda to be published</td></tr>
      </table>
    </body></html>
    """
    events = ietf._parse_upcoming_events_from_important_dates(html)
    assert len(events) == 1
    event = events[0]
    assert event["number"] == "127"
    assert event["dates"] == "2026-11-14"
    assert event["place"] == "San Francisco, US"
    assert event["place"] != "Monday"
