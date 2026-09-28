"""Extract reviewed Bybit request schemas from a pinned official docs checkout."""

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit


def clean(value: str) -> str:
    """Remove documentation markup while retaining field text."""
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    return html.unescape(re.sub("<[^>]*>", "", value)).strip().strip("`*")


def snake(value: str) -> str:
    """Convert official identifiers to Python argument names."""
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value).replace("-", "_").lower()


def extract(root: Path, inventory: dict, targets: set[str]) -> list[dict]:
    """Read each endpoint's own parameter table and HTTP request example."""
    result = []
    for endpoint in inventory["endpoints"]:
        if endpoint["method"] + " " + endpoint["path"] not in targets:
            continue
        relative = endpoint["official_source"].split("/docs/", 1)[1]
        path = root / (relative + ".mdx")
        if not path.exists():
            path = root / (relative + ".md")
        source = path.read_text(encoding="utf-8")
        start = source.index('url="' + endpoint["path"] + '"')
        text = source[start:]
        stop = text.find("<APIEndpoint")
        if stop >= 0:
            text = text[:stop]
        match = re.search(
            r"#{3,4} Request Parameters(.*?)(?=#{3,4} (?:Response|Request Example)|\Z)",
            text,
            re.S,
        )
        if match is None:
            raise ValueError(f"No parameter section: {relative}")
        section = match[1]
        entries = []
        for line in section.splitlines():
            if line.strip().startswith("|"):
                cells = re.split(r"(?<!\\)\|", line.strip())[1:]
                if len(cells) >= 4:
                    entries.append(cells[:4])
        for row in re.findall(r"<tr>(.*?)</tr>", section, re.S):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
            if len(cells) >= 4:
                entries.append(cells[:4])
        fields = []
        for raw_name, raw_required, raw_type, description in entries:
            name = clean(raw_name)
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z_0-9]*", name):
                continue
            if name.lower() == "parameter" or any(f["name"] == name for f in fields):
                continue
            required = clean(raw_required).lower()
            if required not in {"true", "false", "conditional"}:
                raise ValueError(f"Unknown required flag: {relative}/{name}: {required}")
            fields.append(
                {
                    "name": name,
                    "python_name": snake(name)
                    + ("_" if name in {"type", "from", "list", "self", "async"} else ""),
                    "type": clean(raw_type).lower(),
                    "required": required == "true",
                    "description": clean(description),
                }
            )
        verb = "get" if endpoint["method"] == "GET" else "post"
        name = verb + "_" + snake(endpoint["path"].removeprefix("/v5/").replace("/", "_"))
        requests = re.findall(r"```http\s*(.*?)```", text, re.S)
        example = {}
        found = False
        for request in requests:
            if endpoint["path"] not in request.splitlines()[0]:
                continue
            if "{" in request:
                try:
                    example = json.loads(request[request.index("{") :])
                    found = True
                except json.JSONDecodeError:
                    pass
            elif endpoint["method"] == "GET":
                url = request.splitlines()[0].split()[1]
                example = dict(parse_qsl(urlsplit(url).query))
                found = True
            break
        result.append(
            {
                **endpoint,
                "name": name,
                "public": not any("X-BAPI-SIGN" in request for request in requests),
                "fields": fields,
                "example": example,
                "has_example": found,
                "source_file": path.relative_to(root).as_posix(),
            }
        )
    return result


def main() -> None:
    """Extract a draft for review; never mark ledger rows implemented."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    inventory = json.loads(
        Path("docs/official-endpoint-inventory/bybit.json").read_text(encoding="utf-8")
    )
    ledger = json.loads(Path("docs/endpoint-coverage-ledger.json").read_text(encoding="utf-8"))
    targets = {
        row["endpoint"]
        for row in ledger["rows"]
        if row["exchange"] == "bybit" and row["status"] in {"pending", "excluded"}
    } - {"GET /v5/position/list"}
    result = extract(args.checkout / "docs", inventory, targets)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Extracted {len(result)} endpoint drafts; review before generating wrappers.")


if __name__ == "__main__":
    main()
