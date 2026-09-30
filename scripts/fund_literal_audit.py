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
    if re.search(
        r"withdraw|send_(?:usd|spot|asset|to_evm)|usd_?send|spot_?send|send_?asset|send_?to_?evm|bridge",
        name,
    ):
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


def balanced_end(clean: str, start: int) -> int:
    """Find the end of a balanced Rust delimiter group."""
    stack = []
    for index in range(start, len(clean)):
        char = clean[index]
        if char in "([{":
            stack.append(char)
        elif char in ")]}":
            stack.pop()
            if not stack:
                return index + 1
    return len(clean)


def production_source(source: str) -> str:
    """Mask only the attributed test item, including semicolon-only items."""
    clean = masked(source)
    spans = []
    for match in re.finditer(r"#\s*\[\s*cfg\s*\(\s*test\s*\)\s*\]", clean):
        start = match.end()
        while attribute := re.match(r"\s*#\s*\[", clean[start:]):
            start = balanced_end(clean, start + attribute.end() - 1)
        end = re.search(r"[;{]", clean[start:])
        if end is None:
            continue
        stop = start + end.start()
        stop = stop + 1 if clean[stop] == ";" else balanced_end(clean, stop)
        spans.append((match.start(), stop))
    for start, end in reversed(spans):
        source = source[:start] + " " * (end - start) + source[end:]
    return source


def string_parts(source: str) -> list[str]:
    """Read actual Rust string literals, ignoring comments and character tokens."""
    return [decode(t[0]) for t in TOKENS.finditer(source) if t[0].startswith(('"', 'r"', "r#"))]


def fund_fragments(parts: list[str]) -> bool:
    """Recognise split fund identifiers and paths around format placeholders."""
    if any(domain(part) for part in parts) or domain("".join(parts)):
        return True
    words = [word.lower() for part in parts for word in re.findall(r"[a-zA-Z]+", part)]
    return any(
        any(left.endswith(word[:cut]) for left in words)
        and any(right.startswith(word[cut:]) for right in words)
        for word in (
            "withdraw",
            "transfer",
            "usdsend",
            "spotsend",
            "sendasset",
            "sendtoevm",
            "bridge",
        )
        for cut in range(2, len(word) - 1)
    )


def runtime_context(source: str, position: int) -> str:
    """Include preceding local bindings used by a string assembly statement."""
    context = statement(source, position)
    clean = masked(source)
    braces = []
    for index, char in enumerate(clean[:position]):
        if char == "{":
            braces.append(index)
        elif char == "}" and braces:
            braces.pop()
    start = braces[-1] + 1 if braces else 0
    bindings = list(re.finditer(r"\blet\s+(?:mut\s+)?(\w+)\b", clean[start:position]))
    for binding in reversed(bindings):
        if re.search(r"\b" + re.escape(binding[1]) + r"\b", masked(context)):
            value = statement(source, start + binding.start())
            if value not in context:
                context = value + "\n" + context
    return context


def occurrences(source: str, filename: str) -> Iterator[dict[str, str]]:
    """Enumerate fund literals, concatenations, and runtime byte constructions."""
    source = production_source(source)
    clean = masked(source)
    candidates = []
    assembly_contexts = {}
    for token in TOKENS.finditer(source):
        raw = token[0]
        if raw.startswith(('"', 'r"', "r#")):
            name = decode(raw)
            if (re.fullmatch(r"\w+", name) or "/" in name) and domain(name):
                candidates.append((name, token.start()))
    for match in re.finditer(r"\bconcat!\s*([([{])", clean):
        end = balanced_end(clean, match.end() - 1)
        parts = string_parts(source[match.end() : end - 1])
        name = "".join(parts)
        if fund_fragments(parts):
            candidates.append((name, match.start()))
    runtime_names = re.finditer(
        r"\b(?:from_utf8(?:_unchecked|_lossy)?|from_utf16\w*|from_iter)\s*\(|\bchar\s*::\s*from\w*\s*\(|\bas\s+char\b|\.collect\s*::\s*<\s*String\s*>\s*\(",
        clean,
    )
    candidates.extend(("<runtime-string>", match.start()) for match in runtime_names)
    for match in re.finditer(r"\bformat!\s*[([{]|\+|\.\s*(?:push_str|concat|join)\s*\(", clean):
        context = runtime_context(source, match.start())
        if fund_fragments(string_parts(context)):
            candidates.append(("<runtime-string>", match.start()))
            assembly_contexts[match.start()] = context
    seen = set()
    for name, position in candidates:
        if (owner := domain(name)) is not None and re.fullmatch(
            r"crates/dcex/src/exchanges/[^/]+/" + owner + r"\.rs", filename
        ):
            continue
        context = assembly_contexts.get(position, statement(source, position))
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
        for entry in occurrences(path.read_text(encoding="utf8"), path.relative_to(root).as_posix())
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
