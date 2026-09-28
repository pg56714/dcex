"""Extract Bitget operation schemas from its public documentation pages."""

import argparse
import json
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def operations(value: object) -> Iterator[dict[str, Any]]:
    """Yield complete operation objects, excluding navigation summaries."""
    if isinstance(value, dict):
        if all(
            key in value for key in ("operationId", "path", "method", "parameters", "requestBody")
        ):
            yield value
        for child in value.values():
            yield from operations(child)
    elif isinstance(value, list):
        for child in value:
            yield from operations(child)


def read_page(url: str) -> list[dict[str, Any]]:
    """Read the documented JSON hydration payload without executing JavaScript."""
    if not url.startswith("https://www.bitget.com/"):
        raise ValueError("Expected official Bitget HTTPS documentation")
    request = Request(url, headers={"User-Agent": "dcex-documentation-audit/1.0"})  # noqa: S310 - validated HTTPS origin.
    with urlopen(request, timeout=45) as response:  # noqa: S310 - validated HTTPS origin.
        text = response.read().decode("utf-8")
    payload = text.split("window.ZUDOKU_DATA=", 1)[1]
    data, _ = json.JSONDecoder().raw_decode(payload)
    return list(operations(data))


def main() -> None:
    """Regenerate the committed artifacts from the documented source data."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/official-endpoint-inventory/sources/bitget-operations.json",
    )
    args = parser.parse_args()
    inventory = json.loads(
        (ROOT / "docs/official-endpoint-inventory/bitget.json").read_text(encoding="utf-8")
    )
    endpoints = [e for e in inventory["endpoints"] if e["method"] != "WS"]
    urls = sorted({e["official_source"].split("#")[0] for e in endpoints})
    found = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for url, entries in zip(urls, pool.map(read_page, urls), strict=True):
            for operation in entries:
                key = (operation["method"].upper(), operation["path"])
                found[key] = {**operation, "official_source": url + "#" + operation["slug"]}
    missing = [e for e in endpoints if (e["method"], e["path"]) not in found]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {"operations": list(found.values()), "missing": missing}, ensure_ascii=False, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Collected {len(found)} operations; {len(missing)} missing.")


if __name__ == "__main__":
    main()
