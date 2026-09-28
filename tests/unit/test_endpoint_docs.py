"""Keep the generated endpoint coverage page in sync with its ledger."""

from __future__ import annotations

import json

from scripts.build_endpoint_docs import LEDGER, OUTPUT, build_html


def test_endpoint_coverage_html_matches_ledger() -> None:
    """Fail when the ledger changed without regenerating the HTML page."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    assert OUTPUT.read_text(encoding="utf-8") == build_html(ledger), (
        "docs/endpoint-coverage.html is stale; run `python scripts/build_endpoint_docs.py`"
    )


def test_endpoint_coverage_html_embeds_every_ledger_row() -> None:
    """Every ledger row and exchange reaches the page data."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    html = build_html(ledger)
    start = html.index('<script id="data" type="application/json">') + len(
        '<script id="data" type="application/json">'
    )
    payload = json.loads(html[start : html.index("</script>", start)].replace("<\\/", "</"))

    assert len(payload["rows"]) == len(ledger["rows"])
    assert set(payload["exchanges"]) == {row["exchange"] for row in ledger["rows"]}
    assert "</script" not in html[start : html.index("</script>", start)]
