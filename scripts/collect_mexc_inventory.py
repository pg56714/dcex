"""Collect endpoint URLs and request tables from MEXC's public documentation."""

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


class Page(HTMLParser):
    """Read only article text and navigation within the English API documentation."""

    def __init__(self) -> None:
        super().__init__()
        self.article = False
        self.text: list[str] = []
        self.links: set[str] = set()
        self.tables: list[list[list[str]]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect article elements and official navigation links."""
        if tag == "a":
            href = dict(attrs).get("href") or ""
            if href.startswith(("/api-docs/spot-v3/", "/api-docs/futures/")):
                self.links.add(href.split("#")[0])
        if tag == "article":
            self.article = True
        if self.article:
            if tag == "table":
                self.tables.append([])
            if tag == "tr":
                self.row = []
            if tag in {"td", "th"}:
                self.cell = []

    def handle_endtag(self, tag: str) -> None:
        """Preserve table cells separately from rendered article text."""
        if tag == "article":
            self.article = False
        if self.article:
            if tag in {"td", "th"} and self.cell is not None:
                if self.row is not None:
                    self.row.append("".join(self.cell).strip())
                self.cell = None
            if tag == "tr" and self.row is not None:
                self.tables[-1].append(self.row)
                self.row = None
            self.text.append(" ")

    def handle_data(self, data: str) -> None:
        """Read visible article and table contents."""
        if self.article:
            self.text.append(data)
            if self.cell is not None:
                self.cell.append(data)


def fetch(path: str) -> tuple[str, Page, str]:
    """Fetch a public documentation page; no exchange account API is used."""
    if not path.startswith(("/api-docs/spot-v3/", "/api-docs/futures/")):
        raise ValueError("Only official MEXC documentation paths are allowed")
    url = "https://www.mexc.com" + path
    request = Request(url, headers={"User-Agent": "dcex-documentation-review"})  # noqa: S310
    with urlopen(request, timeout=20) as response:  # noqa: S310
        content = response.read()
    page = Page()
    page.feed(content.decode("utf-8"))
    return path, page, hashlib.sha256(content).hexdigest()


def main() -> None:
    """Save a reproducible inventory for review, without changing ledger statuses."""
    pending = {"/api-docs/spot-v3/introduction", "/api-docs/futures/integration-guide"}
    seen: set[str] = set()
    pages = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        while pending:
            batch = sorted(pending - seen)
            if not batch:
                break
            seen.update(batch)
            if len(seen) > 300:
                raise ValueError(
                    "Unexpected documentation scope; review navigation before continuing"
                )
            pending = set()
            for path, page, digest in pool.map(fetch, batch):
                pending.update(page.links - seen)
                text = re.sub(r"\s+", " ", "".join(page.text)).strip()
                routes = list(
                    dict.fromkeys(
                        match[0].upper() + " " + match[1].rstrip(".,")
                        for match in re.findall(
                            r"\b(GET|POST|PUT|DELETE|PATCH)\s+(/api/[^\s`?]+)", text, re.I
                        )
                    )
                )
                pages.append(
                    {
                        "official_source": "https://www.mexc.com" + path,
                        "sha256": digest,
                        "routes": routes,
                        "primary_route": (
                            match.group(1).upper() + " /" + match.group(2).lstrip("/")
                            if (
                                match := re.search(
                                    r"HTTP Request\s+(GET|POST|PUT|DELETE|PATCH)"
                                    r"\s+(/?/?api/[^\s`?]+)",
                                    text,
                                    re.I,
                                )
                            )
                            else None
                        ),
                        "text": text,
                        "tables": page.tables,
                    }
                )
            print(f"Read {len(pages)} documentation pages; {len(pending)} remaining", flush=True)
    output = Path(".tmp/mexc-documentation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(pages, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
