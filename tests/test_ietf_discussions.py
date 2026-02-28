import json

from ietf_wg_agent import ietf


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("http error")

    def json(self):
        return json.loads(self.text)


def test_fetch_wg_discussions_last_months_filters_old_posts(monkeypatch):
    html = """
    <html><body>
      <div>
        <a href="/arch/msg/lsr/abc123/">Thread A: draft-ietf-lsr-a</a>
        <time datetime="2099-01-10T12:00:00Z">2099-01-10</time>
        <span>from: Alice</span>
      </div>
      <div>
        <a href="/arch/msg/lsr/old999/">Old thread</a>
        <time datetime="2000-01-01T00:00:00Z">2000-01-01</time>
        <span>from: Bob</span>
      </div>
    </body></html>
    """

    def fake_get(url, timeout=20):
        assert url.endswith("/arch/browse/lsr/")
        return _FakeResponse(html)

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    posts = ietf.fetch_wg_discussions_last_months("lsr", months=3)
    assert len(posts) == 1
    assert posts[0].subject.startswith("Thread A")
    assert posts[0].author == "Alice"


def test_fetch_wg_discussions_last_day_excludes_unknown_or_old(monkeypatch):
    html = """
    <html><body>
      <div>
        <a href="/arch/msg/lsr/new1/">Recent thread</a>
        <time datetime="2099-01-10T12:00:00Z">2099-01-10</time>
        <span>from: Alice</span>
      </div>
      <div>
        <a href="/arch/msg/lsr/old1/">Old thread</a>
        <time datetime="2000-01-01T00:00:00Z">2000-01-01</time>
        <span>from: Bob</span>
      </div>
      <div>
        <a href="/arch/msg/lsr/nodate1/">No date thread</a>
        <span>from: Carol</span>
      </div>
    </body></html>
    """

    def fake_get(url, timeout=20):
        assert url.endswith("/arch/browse/lsr/")
        return _FakeResponse(html)

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    posts = ietf.fetch_wg_discussions_last_day("lsr", days=1)
    assert len(posts) == 1
    assert posts[0].subject == "Recent thread"


def test_summarize_discussions_output():
    posts = [
        ietf.DiscussionPost(
            date="2099-01-10",
            subject="LSR draft discussion: foo",
            author="Alice",
            url="https://mailarchive.ietf.org/arch/msg/lsr/abc123/",
        ),
        ietf.DiscussionPost(
            date="2099-01-11",
            subject="LSR draft discussion: bar",
            author="Bob",
            url="https://mailarchive.ietf.org/arch/msg/lsr/def456/",
        ),
    ]

    from ietf_wg_agent.summarizer import summarize_discussions

    summary = summarize_discussions(posts, months=3)
    assert "Draft discussions summary (last 3 months):" in summary
    assert "Total discussion posts: 2" in summary
    assert "Recent discussion threads:" in summary
