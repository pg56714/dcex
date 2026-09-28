"""
Build docs/endpoint-coverage.html from docs/endpoint-coverage-ledger.json.

Edit the ledger JSON, then run ``python scripts/build_endpoint_docs.py``.
``--check`` exits non-zero when the committed HTML is out of date.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "endpoint-coverage-ledger.json"
OUTPUT = ROOT / "docs" / "endpoint-coverage.html"
TEMPLATE = Path(__file__).with_name("endpoint_coverage_template.html")

EXCHANGE_ORDER = [
    "binance",
    "bybit",
    "okx",
    "bitget",
    "bingx",
    "kraken",
    "mexc",
    "kucoin",
    "hyperliquid",
    "lighter",
    "backpack",
    "aster",
    "extended",
    "ondo",
    "arcus",
]


def _flag(value: object) -> int:
    """Encode a tri-state support flag as 1, 0 or -1 (unknown)."""
    if value is True:
        return 1
    if value is False:
        return 0
    return -1


def _compact_rows(rows: list[dict[str, Any]], exchanges: list[str]) -> list[list[Any]]:
    """Reduce ledger rows to the fields the page renders."""
    index = {name: i for i, name in enumerate(exchanges)}
    return [
        [
            row["row"],
            index[row["exchange"]],
            row.get("kind", ""),
            row.get("category", ""),
            row.get("endpoint", ""),
            row.get("status", ""),
            row.get("methods") or [],
            row.get("note", ""),
            row.get("official_source", ""),
            _flag(row.get("rust")),
            _flag(row.get("python_sync")),
            _flag(row.get("python_async")),
        ]
        for row in rows
    ]


def _exchange_list(rows: list[dict[str, Any]]) -> list[str]:
    """Return exchanges in the documented order, followed by any new ones."""
    seen = {row["exchange"] for row in rows}
    ordered = [name for name in EXCHANGE_ORDER if name in seen]
    return ordered + sorted(seen - set(ordered))


def build_html(ledger: dict[str, Any]) -> str:
    """Render the full HTML page for a ledger document."""
    rows = ledger["rows"]
    exchanges = _exchange_list(rows)
    payload = {
        "reviewed": ledger.get("reviewed", ""),
        "verification": ledger.get("verification", {}),
        "exchanges": exchanges,
        "rows": _compact_rows(rows, exchanges),
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")
    return TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", data)


def main() -> int:
    """Write the HTML, or verify it is current with ``--check``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the HTML is stale")
    args = parser.parse_args()

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    html = build_html(ledger)
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != html:
            print(f"{OUTPUT.relative_to(ROOT)} is out of date; run scripts/build_endpoint_docs.py")
            return 1
        return 0
    OUTPUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(ledger['rows'])} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
