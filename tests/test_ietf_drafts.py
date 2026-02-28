import pytest
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


def test_extract_abstract_from_doc_page():
    html = """
    <html><body>
      <h2>Abstract</h2>
      <p>This draft specifies a routing extension.</p>
      <h2>Authors</h2>
    </body></html>
    """
    abstract = ietf._extract_abstract_from_doc_page(html)
    assert "routing extension" in abstract


def test_extract_status_from_doc_page():
    html = """
    <html><body>
      <h2>Status</h2>
      <p>WG Consensus: Waiting for Write-Up Reviews</p>
      <h2>Abstract</h2>
      <p>Some abstract text.</p>
    </body></html>
    """
    status = ietf._extract_status_from_doc_page(html)
    assert "WG Consensus: Waiting for Write-Up Reviews" in status


def test_fetch_top_active_drafts_from_documents_page(monkeypatch):
    docs_html = """
    <html><body><table>
      <tr>
        <td><a href="/doc/draft-ietf-idr-first/">17 pages draft-ietf-idr-first-01 Example First Draft</a></td>
        <td>2025-10-17</td>
        <td>WG Consensus: Waiting for Write-Up Reviews</td>
      </tr>
      <tr><td><a href="/doc/draft-ietf-idr-second/">draft-ietf-idr-second</a></td><td>2025-09-17</td><td>WG Document : Proposed Standard Reviews</td></tr>
      <tr><td><a href="/doc/draft-ietf-idr-third/">draft-ietf-idr-third</a></td><td>2025-08-17</td><td>In WG Last Call : Proposed Standard</td></tr>
      <tr><td><a href="/doc/draft-ietf-idr-fourth/">draft-ietf-idr-fourth</a></td><td>2025-07-17</td><td>WG Document</td></tr>
      <tr><td><a href="/doc/draft-ietf-idr-fifth/">draft-ietf-idr-fifth</a></td><td>2025-06-17</td><td>WG Document</td></tr>
      <tr><td><a href="/doc/draft-ietf-idr-sixth/">draft-ietf-idr-sixth</a></td><td>2025-05-17</td><td>WG Document</td></tr>
    </table></body></html>
    """

    def _doc_html(name: str) -> str:
        return f"""
        <html><body>
          <h2>Status</h2>
          <p>WG Document : Proposed Standard Reviews</p>
          <h2>Abstract</h2>
          <p>Abstract for {name}</p>
        </body></html>
        """

    def fake_get(url, params=None, timeout=20):
        if url == ietf.DOC_API_URL and params and str(params.get("name", "")).startswith(
            "draft-ietf-idr-"
        ):
            name = params["name"]
            return _FakeResponse(
                f'{{"objects":[{{"name":"{name}","title":"API title for {name}","abstract":"API abstract for {name}"}}]}}'
            )
        if url.endswith("/wg/idr/documents/"):
            return _FakeResponse(docs_html)
        if "/doc/draft-ietf-idr-" in url:
            name = url.rstrip("/").split("/")[-1]
            return _FakeResponse(_doc_html(name))
        pytest.fail(f"Unexpected URL: {url}")

    monkeypatch.setattr(ietf.requests, "get", fake_get)

    drafts = ietf.fetch_top_active_drafts("idr", limit=5)
    assert len(drafts) == 5
    assert drafts[0].name == "draft-ietf-idr-first"
    assert drafts[0].title in {
        "Example First Draft",
        "API title for draft-ietf-idr-first",
    }
    assert drafts[0].status == "WG Consensus: Waiting for Write-Up Reviews"
    assert drafts[1].status == "WG Document : Proposed Standard Reviews"
    assert "Abstract for draft-ietf-idr-first" in drafts[0].abstract


def test_extract_status_and_title_from_row_text():
    row = (
        "17 pages draft-ietf-bess-ebgp-dmz-08 "
        "BGP link bandwidth extended community use cases 2025-10-17 "
        "I-D Exists WG Document Jeffrey Haas"
    )
    title = ietf._extract_title_from_row_text(row, "draft-ietf-bess-ebgp-dmz")
    status = ietf._extract_status_from_row_text(row)
    assert title == "BGP link bandwidth extended community use cases"
    assert status == "WG Document"
