"""Extract official WebSocket request examples from an OKX documentation snapshot."""

import argparse
import json
import re
from pathlib import Path

from scripts.extract_slate_inventory import text

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Regenerate the committed artifacts from the documented source data."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    html = args.source.read_text(encoding="utf-8")
    headings = list(
        re.finditer(r"<h([1-6])\b[^>]*id=['\"]([^'\"]+)['\"][^>]*>(.*?)</h[1-6]>", html, re.S)
    )
    sections = {
        h[2]: html[
            h.end() : next(
                (later.start() for later in headings[i + 1 :] if later[1] <= h[1]), len(html)
            )
        ]
        for i, h in enumerate(headings)
    }
    ledger = json.loads((ROOT / "docs/endpoint-coverage-ledger.json").read_text(encoding="utf-8"))
    operations = []
    for row in ledger["rows"]:
        if row["exchange"] != "okx" or row["kind"] != "WS" or row["row"] < 4761:
            continue
        anchor = row["official_source"].split("#")[1]
        section = sections[anchor]
        examples = []
        for raw in re.findall(r"<pre\b[^>]*>.*?<code\b[^>]*>(.*?)</code>.*?</pre>", section, re.S):
            content = text(raw)
            try:
                obj = json.loads(content)
            except ValueError:
                continue
            if isinstance(obj, dict) and obj.get("op"):
                examples.append(obj)
        operations.append(
            {
                "row": row["row"],
                "source": row["official_source"],
                "examples": examples,
                "text": text(section),
            }
        )
    (ROOT / "docs/official-endpoint-inventory/sources/okx-ws.json").write_text(
        json.dumps(operations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for op in operations:
        print(op["row"], [(e["op"], e.get("args")) for e in op["examples"]])


if __name__ == "__main__":
    main()
