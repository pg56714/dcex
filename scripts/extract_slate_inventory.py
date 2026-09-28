"""Extract endpoint sections from an official Slate HTML documentation snapshot."""

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path


class Text(HTMLParser):
    """Read visible text while preserving table cell content."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        """Collect text without evaluating scripts."""
        self.parts.append(data)


def text(html: str) -> str:
    """Return normalized visible text."""
    parser = Text()
    parser.feed(html)
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def extract(source: Path, base_url: str, level: int) -> dict:
    """Read request sections and keep source anchors and table data."""
    raw = source.read_bytes()
    html = raw.decode("utf-8")
    headings = list(
        re.finditer(rf"<h{level}\b[^>]*id=['\"]([^'\"]+)['\"][^>]*>(.*?)</h{level}>", html, re.S)
    )
    endpoints = []
    for i, heading in enumerate(headings):
        section = html[
            heading.end() : headings[i + 1].start() if i + 1 < len(headings) else len(html)
        ]
        requests = re.findall(
            r"<code>\s*(GET|POST|PUT|DELETE|PATCH)\s+(/[^<\s]+)\s*</code>", section
        )
        if not requests:
            continue
        tables = [
            [
                [text(cell) for cell in re.findall(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", row, re.S)]
                for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", table, re.S)
            ]
            for table in re.findall(r"<table\b[^>]*>(.*?)</table>", section, re.S)
        ]
        examples = [
            text(code)
            for code in re.findall(
                r"<pre\b[^>]*>.*?<code\b[^>]*>(.*?)</code>.*?</pre>", section, re.S
            )
        ]
        for method, path in dict.fromkeys(requests):
            endpoints.append(
                {
                    "method": method,
                    "path": path,
                    "title": text(heading[2]),
                    "official_source": base_url.rstrip("#") + "#" + heading[1],
                    "tables": tables,
                    "examples": examples,
                    "text": text(section),
                }
            )
    return {
        "source": base_url,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "endpoints": endpoints,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("base_url")
    parser.add_argument("output", type=Path)
    parser.add_argument("--level", type=int, default=3)
    args = parser.parse_args()
    args.output.write_text(
        json.dumps(extract(args.source, args.base_url, args.level), indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
