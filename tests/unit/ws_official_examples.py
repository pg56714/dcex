"""Read JSON examples from committed official protocol snapshots."""

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def load_operations(exchange: str) -> list[dict[str, Any]]:
    """Load the official message descriptions independently of native code."""
    path = ROOT / f"docs/official-endpoint-inventory/sources/{exchange}-ws.json"
    return json.loads(path.read_text(encoding="utf-8"))


def json_examples(text: str) -> list[dict[str, Any] | list[Any]]:
    """Decode JSON fences, tolerating documentation comments and trailing commas."""
    result = []
    for block in re.findall(r"```(?:json|javascript)[^\n]*\n(.*?)```", text, re.S):
        block = re.sub(r'("(?:[^"\\]|\\.)*")|//[^\n]*|#[^\n]*', lambda m: m[1] or "", block)
        block = re.sub(r",\s*([}\]])", r"\1", block)
        decoder = json.JSONDecoder()
        position = 0
        while position < len(block):
            match = re.search(r"[\[{]", block[position:])
            if match is None:
                break
            start = position + match.start()
            try:
                value, end = decoder.raw_decode(block, start)
            except json.JSONDecodeError:
                position = start + 1
                continue
            if isinstance(value, dict | list):
                result.append(value)
            position = end
    return result
