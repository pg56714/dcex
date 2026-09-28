"""Collect KuCoin's structured official request schemas without executing page scripts."""

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def decode_operation(page: str) -> dict[str, Any]:
    """Decode the structured operation embedded in a documentation page."""
    match = re.search(r'\.enqueue\(("(?:[^"\\]|\\.)*")\)', page)
    if not match:
        raise ValueError("Official page contains no structured document payload")
    nodes = json.loads(json.loads(match[1]))
    cache = {}

    def decode(index: int) -> Any:  # noqa: ANN401 - heterogeneous serialized document graph.
        if index < 0:
            return None
        if index in cache:
            return cache[index]
        value = nodes[index]
        if isinstance(value, dict):
            result = {}
            cache[index] = result
            result.update({decode(int(k[1:])): decode(v) for k, v in value.items()})
        elif isinstance(value, list):
            result = [decode(i) for i in value]
        else:
            result = value
        cache[index] = result
        return result

    for index, node in enumerate(nodes):
        if isinstance(node, dict):
            keys = {nodes[int(k[1:])] for k in node if k.startswith("_")}
            if {"method", "path", "requestBody", "parameters"} <= keys:
                return decode(index)
    raise ValueError("No API operation in official page")


def collect(row: dict[str, Any]) -> dict[str, Any]:
    """Fetch and verify one official operation against its ledger route."""
    url = row["official_source"]
    if not url.startswith("https://www.kucoin.com/docs-new/"):
        raise ValueError("Unexpected official documentation origin")
    with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as response:  # noqa: S310 - official HTTPS origin checked above.
        operation = decode_operation(response.read().decode("utf-8"))
    if operation["path"] != row["path"] or operation["method"].upper() != row["http_method"]:
        raise ValueError(
            f"Route changed for row {row['row']}: {operation['method']} {operation['path']}"
        )
    return {
        "row": row["row"],
        "official_source": url,
        **{
            k: operation.get(k)
            for k in (
                "name",
                "description",
                "method",
                "path",
                "auth",
                "parameters",
                "requestBody",
                "codeSamples",
                "customApiFields",
            )
        },
    }


def main() -> None:
    """Regenerate the committed artifacts from the documented source data."""
    ledger = json.loads((ROOT / "docs/endpoint-coverage-ledger.json").read_text(encoding="utf-8"))
    existing = ROOT / "docs/official-endpoint-inventory/sources/kucoin-operations.json"
    selected = {op["row"] for op in json.loads(existing.read_text(encoding="utf-8"))}
    rows = [
        r
        for r in ledger["rows"]
        if r["exchange"] == "kucoin" and r["kind"] == "REST" and r["row"] in selected
    ]
    with ThreadPoolExecutor(max_workers=5) as pool:
        operations = list(pool.map(collect, rows))
    (ROOT / "docs/official-endpoint-inventory/sources/kucoin-operations.json").write_text(
        json.dumps(operations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Collected {len(operations)} official request schemas.")


if __name__ == "__main__":
    main()
