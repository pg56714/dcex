"""Check explicit statement-level fund exceptions; additions require an approval file."""

import argparse
import hashlib
import json
import re
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "tests/fixtures/fund_literal_allowlist.json"
TOKENS = re.compile(
    r'''//[^\n]*|/\*[\s\S]*?\*/|r(?P<hash>\#*)"[\s\S]*?"(?P=hash)|'(?:\\.|[^'\\\n])'|"(?:\\[\s\S]|[^"\\])*"'''
)


def masked(source: str) -> str:
    """Keep offsets while hiding comments, character literals and strings."""
    return TOKENS.sub(lambda m: "".join("\n" if c == "\n" else " " for c in m[0]), source)


def domain(name: str) -> str | None:
    """Classify identifiers and endpoint paths, including encoded spellings."""
    name = name.lower()
    if re.search(r"withdraw|send_(?:usd|spot|asset|to_evm)|bridge", name):
        return "withdrawals"
    if name in {
        "transfer_l2_account",
        "transfer_same_master_account",
        "sign_transfer_l2_account",
        "sign_transfer_same_master_account",
        "transfer_master_internal",
        "transfer_sub_account_internal",
    }:
        return "withdrawals"
    return "transfers" if "transfer" in name else None


def decode(raw: str) -> str:
    """Decode Rust identifier escapes without interpreting arbitrary code."""
    value = raw[raw.index('"') + 1 : raw.rindex('"')]
    if raw.startswith('"'):
        value = re.sub(r"\\\r?\n\s*", "", value)
        value = re.sub(
            r"\\x([0-9a-fA-F]{2})|\\u\{([0-9a-fA-F]+)\}",
            lambda m: chr(int(m[1] or m[2], 16)),
            value,
        )
    return value


def statement(source: str, position: int) -> str:
    """Return the complete statement/arm in the innermost brace container."""
    clean = masked(source)
    braces = []
    for index, char in enumerate(clean[:position]):
        if char == "{":
            braces.append(index)
        elif char == "}" and braces:
            braces.pop()
    start = braces[-1] + 1 if braces else 0
    # Wrapper macros group entries inside public/private brackets. Pin one
    # complete wrapper entry, not the whole macro or just its field literal.
    for group in re.finditer(r"\b(?:public|private)\s*\[", clean[:position]):
        level = 1
        end = group.end()
        while level and end < position:
            level += (clean[end] == "[") - (clean[end] == "]")
            end += 1
        if level and group.end() > start:
            start = group.end()
    depth = []
    for end in range(start, len(clean)):
        char = clean[end]
        if char in "([{":
            depth.append(char)
        elif char in ")]}":
            if not depth:
                return source[start:end].strip()
            depth.pop()
        block_end = (
            char == "}"
            and not depth
            and re.match(
                r"\s*(?:(?:if|for|while|loop|match|impl|struct|enum|(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn)\b|[^{;]*=>\s*\{)",
                clean[start:end],
            )
            and not re.match(r"\s*else\b", clean[end + 1 :])
        )
        if not depth and (char in ",;" or block_end):
            if end >= position:
                return source[start : end + 1].strip()
            start = end + 1
    return source[start:].strip()


def production_source(source: str) -> str:
    """Exclude test-only blocks without hiding production code that follows."""
    clean = masked(source)
    spans = []
    for match in re.finditer(r"#\s*\[\s*cfg\(test\)\s*\]", clean):
        start = clean.find("{", match.end())
        if start < 0:
            continue
        end, depth = start + 1, 1
        while depth and end < len(clean):
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        spans.append((match.start(), end))
    for start, end in reversed(spans):
        source = source[:start] + " " * (end - start) + source[end:]
    return source


def occurrences(source: str, filename: str) -> Iterator[dict[str, str]]:
    """Enumerate fund literals, concatenations, and runtime byte constructions."""
    source = production_source(source)
    clean = masked(source)
    candidates = []
    for token in TOKENS.finditer(source):
        raw = token[0]
        if raw.startswith(('"', 'r"', "r#")):
            name = decode(raw)
            if (re.fullmatch(r"\w+", name) or "/" in name) and domain(name):
                candidates.append((name, token.start()))
    for match in re.finditer(r"\bconcat!\s*\((.*?)\)", source, re.S):
        if not clean[match.start() :].startswith("concat!"):
            continue
        parts = [
            decode(t[0]) for t in TOKENS.finditer(match[1]) if t[0].startswith(('"', 'r"', "r#"))
        ]
        name = "".join(parts)
        if domain(name) or any(domain(part) for part in parts):
            candidates.append((name, match.start()))
    # Dynamically assembled names have no auditable literal. Require an explicit
    # exception for the conversion statement even when the bytes are not constant.
    runtime_names = re.finditer(
        r"\b(?:from_utf8(?:_unchecked|_lossy)?|from_iter)\s*\(|\bas\s+char\b|\.collect\s*::\s*<\s*String\s*>\s*\(",
        clean,
    )
    candidates.extend(("<runtime-string>", match.start()) for match in runtime_names)
    seen = set()
    for name, position in candidates:
        if (owner := domain(name)) is not None and filename == owner + ".rs":
            continue
        context = statement(source, position)
        digest = hashlib.sha256(context.encode()).hexdigest()
        key = name, digest
        if key not in seen:
            seen.add(key)
            yield {"name": name, "sha256": digest, "context": context}


def source_paths(root: Path = ROOT) -> Iterator[Path]:
    """Include exchange-independent transport and Python binding Rust code."""
    for folder in ("crates/dcex/src/exchanges", "crates/dcex/src/ws", "crates/dcex-python/src"):
        for path in sorted((root / folder).rglob("*.rs")):
            if "tests" in path.parts or path.name == "tests.rs" or "generated" in path.parts:
                continue
            yield path


def inventory(root: Path = ROOT) -> list[dict[str, str]]:
    """Build a read-only report; this does not approve any occurrence."""
    return [
        {"source": path.relative_to(root).as_posix(), **entry}
        for path in source_paths(root)
        for entry in occurrences(path.read_text(encoding="utf8"), path.name)
    ]


def identity(entry: dict[str, str]) -> tuple[str, str, str]:
    """Identify an exception independently of its explanation."""
    return entry["source"], entry["name"], entry["sha256"]


def approved_update(
    existing: list[dict[str, str]],
    approvals: dict[str, list[dict[str, str]]],
    observed: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Apply only explicit additions/removals; never invent or replace reasons."""
    result = {identity(entry): entry for entry in existing}
    current = {identity(entry) for entry in observed}
    for entry in approvals.get("remove", []):
        key = identity(entry)
        if result.get(key) != entry:
            raise ValueError("Removal must reproduce the exact existing exception and reason")
        del result[key]
    for entry in approvals.get("add", []):
        key = identity(entry)
        if key not in current or not entry.get("reason", "").strip():
            raise ValueError("An addition needs a current statement hash and an explicit reason")
        if key in result and result[key] != entry:
            raise ValueError("Existing reasons cannot be overwritten")
        result[key] = entry
    return sorted(result.values(), key=identity)


def main() -> int:
    """Report drift by default; write only explicitly approved exception edits."""
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--report", action="store_true")
    modes.add_argument("--write", action="store_true")
    parser.add_argument("--approvals", type=Path)
    args = parser.parse_args()
    observed = inventory()
    if args.report:
        print(json.dumps(observed, ensure_ascii=False, indent=2))
        return 0
    existing = json.loads(ALLOWLIST.read_text(encoding="utf8"))
    if args.write:
        if args.approvals is None:
            parser.error("--write requires an explicit --approvals JSON file")
        existing = approved_update(
            existing, json.loads(args.approvals.read_text(encoding="utf8")), observed
        )
        ALLOWLIST.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
        )
    actual = {identity(entry) for entry in observed}
    pinned = {identity(entry) for entry in existing}
    for key in sorted(actual - pinned):
        print("UNAPPROVED", key)
    for key in sorted(pinned - actual):
        print("STALE", key)
    return int(actual != pinned)


if __name__ == "__main__":
    raise SystemExit(main())
