# Generated Data Schemas

## 1) Subscription DB Schema

File:
- `~/.ietf_wg_agent_subscriptions.json`

Shape:
```json
{
  "users": {
    "user@example.com": {
      "wgs": ["lsr", "bess"]
    }
  }
}
```

## 2) WG Charter Vector DB Schema

File:
- `data/wg_charter_vector_db.json`

Top-level payload:
```json
{
  "schema_version": 1,
  "built_at": "2026-02-28T16:23:55.048935+00:00",
  "checksum": "595fc4f9d71a4e32a6f7a6a84369e5fcf530c27d904828f7a1be712c5791ca57",
  "source": {
    "wg_index_url": "https://datatracker.ietf.org/wg/",
    "wg_about_url_template": "https://datatracker.ietf.org/wg/{acronym}/about/",
    "wg_documents_url_template": "https://datatracker.ietf.org/wg/{acronym}/documents/"
  },
  "stats": {
    "wg_count": 116,
    "term_count": 10848,
    "skipped_wgs": 18,
    "documents_fetch_failures": 0,
    "deleted_previous": true
  },
  "idf": {
    "routing": 1.23
  },
  "documents": [
    {
      "acronym": "rtgwg",
      "name": "Routing Area Working Group",
      "about_url": "https://datatracker.ietf.org/wg/rtgwg/about/",
      "documents_url": "https://datatracker.ietf.org/wg/rtgwg/documents/",
      "charter_text": "Complete charter text ...",
      "documents_text": "Complete documents section text ...",
      "term_freq": {
        "routing": 15,
        "vrrp": 2,
        "bfd": 2
      },
      "vector": {
        "routing": 0.04,
        "vrrp": 0.01,
        "bfd": 0.01
      },
      "vector_norm": 0.78
    }
  ],
  "errors": [],
  "warnings": []
}
```

## Field Notes
- `documents[].charter_text` stores full charter corpus text extracted from WG `/about/` section.
- `documents[].documents_text` stores full text corpus from WG `/documents/` page.
- `term_freq` contains token counts from acronym + name + charter + documents corpus.
- `vector` and `vector_norm` are normalized sparse TF-IDF style values used for cosine similarity matching.
- `errors` captures per-WG hard failures (WG skipped).
- `warnings` captures non-fatal issues (for example documents-page fetch failures).

## Current Artifact Metrics (Latest Rebuild)
- Build timestamp: `2026-02-28T16:23:55.048935+00:00`
- WG entries: `116`
- Terms: `10848`
- File lines: `101859`
- Approx pages at 240 lines/page: `425`
- File bytes: `4348122`
