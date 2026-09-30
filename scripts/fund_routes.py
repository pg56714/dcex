"""Fail closed on nonliteral transport routes; pin existing routing infrastructure."""

import hashlib
import json
import re
from pathlib import Path

from scripts.fund_literal_audit import ROOT, TOKENS, balanced_end, masked, production_source

PINS = ROOT / "tests/fixtures/fund_dynamic_routes.json"
OWNER = re.compile(r"crates/dcex/src/exchanges/[^/]+/(?:withdrawals|transfers)\.rs")


def arguments(source: str, *, types: bool = False) -> list[str]:
    """Split a Rust argument list without splitting nested expressions or types."""
    clean = masked(source)
    stack = []
    start = 0
    result = []
    for index, char in enumerate(clean):
        if char in "([{":
            stack.append(char)
        elif char == "<" and (types or clean[max(0, index - 2) : index] == "::"):
            stack.append(char)
        elif char in ")]}" or char == ">" and stack and stack[-1] == "<":
            if stack:
                stack.pop()
        elif char == "," and not stack:
            result.append(source[start:index].strip())
            start = index + 1
    if source[start:].strip():
        result.append(source[start:].strip())
    return result


def source_scope(path: str) -> str:
    """Resolve the exchange whose client signature determines argument slots."""
    match = re.search(r"crates/dcex/src/exchanges/([^/]+)/", path)
    if match:
        return match[1]
    match = re.search(r"crates/dcex-python/src/clients/(\w+)\.rs", path)
    return match[1] if match else "shared"


def sources(root: Path) -> dict[str, str]:
    """Include generated routes, unlike the separate literal ownership inventory."""
    return {
        p.relative_to(root).as_posix(): production_source(p.read_text(encoding="utf8"))
        for p in sorted((root / "crates").rglob("*.rs"))
        if "src" in p.relative_to(root).parts
        and "tests" not in p.relative_to(root).parts
        and p.name != "tests.rs"
    }


def transport_slots(files: dict[str, str]) -> dict[tuple[str, str], set[int]]:
    """Discover route slots from definitions, including new signed transports."""
    slots = {}
    for path, source in files.items():
        clean = masked(source)
        for match in re.finditer(r"\bfn\s+(\w+)\s*\(", clean):
            end = balanced_end(clean, match.end() - 1)
            params = arguments(source[match.end() : end - 1], types=True)
            params = [p for p in params if not re.fullmatch(r"&?(?:'\w+\s+)?(?:mut\s+)?self", p)]
            protected = bool(
                re.search(
                    r"private|signed|transport|request|submit_action|exchange_payload|"
                    r"additional_user_action|contract_(?:get|post_json)|public_get",
                    match[1],
                )
            )
            indexes = {
                index
                for index, param in enumerate(params)
                if protected
                and (
                    re.match(r"(?:mut\s+)?path\s*:", param)
                    or re.match(
                        r"(?:mut\s+)?(?:method_name|name|instruction|kind|action|payload)\s*:\s*"
                        r"(?:&(?:'\w+\s+)?str\b|String\b|OrderedValue\b|Value\b)",
                        param,
                    )
                )
            }
            if indexes:
                slots.setdefault((source_scope(path), match[1]), set()).update(indexes)
    return slots


def default_slots(name: str) -> set[int]:
    """Protect standalone mutations and references even without a local definition."""
    if name in {"signed_call", "spot_private", "inventory_transport", "private_body_request"}:
        return {1}
    if re.fullmatch(
        r"(?:\w+_)?private_request|private_(?:get|post|put|patch|delete)(?:_\w+)?|"
        r"(?:get|post)_private|(?:submit|additional_user)_action|exchange_payload(?:_at_nonce)?|"
        r"(?:table|catalog|field_schema)_request_transport|contract_(?:get|post_json)",
        name,
    ):
        return {0}
    return set()


def nonliteral_routes(source: str, filename: str, slots: dict) -> list[dict]:
    """Report every nonliteral argument at a protected routing slot."""
    if OWNER.fullmatch(filename):
        return []
    clean = masked(source)
    found = []
    # Taking a transport as a function value must not evade argument inspection.
    for reference in re.finditer(r"(?:::|\.)\s*(\w+)\b(?!\w)", clean):
        name = reference[1]
        if not slots.get((source_scope(filename), name), default_slots(name)):
            continue
        if re.match(r"\s*(?:!\s*)?[(\[{]", clean[reference.end() :]):
            continue
        found.append({"transport": name, "slot": -1, "expression": "indirect transport reference"})
    for match in re.finditer(r"\b(\w+)\s*(?:!\s*)?([([{])", clean):
        # Definitions are declarations, not calls. Their bodies are scanned normally.
        if re.search(r"\bfn\s*$", clean[max(0, match.start() - 10) : match.start()]):
            continue
        name = match[1]
        indexes = slots.get((source_scope(filename), name), default_slots(name))
        if not indexes:
            continue
        end = balanced_end(clean, match.end() - 1)
        args = arguments(source[match.end() : end - 1])
        for index in sorted(indexes):
            if index >= len(args):
                continue
            expression = args[index]
            if TOKENS.fullmatch(expression) and expression.startswith(('"', 'r"', "r#")):
                continue
            found.append({"transport": name, "slot": index, "expression": expression})
    return found


def dependency_hash(files: dict[str, str], scope: str) -> str:
    """Pin helpers/constants too: changing an upstream builder invalidates approval."""
    selected = {p: s for p, s in files.items() if source_scope(p) in {scope, "shared"}}
    return hashlib.sha256(json.dumps(selected, sort_keys=True).encode()).hexdigest()


def inventory(root: Path = ROOT) -> list[dict]:
    """Report existing nonliteral routes without approving or writing them."""
    files = sources(root)
    slots = transport_slots(files)
    hashes = {scope: dependency_hash(files, scope) for scope in {source_scope(p) for p in files}}
    return [
        {
            "source": path,
            "sha256": hashlib.sha256(source.encode()).hexdigest(),
            "dependencies": hashes[source_scope(path)],
            "routes": routes,
        }
        for path, source in files.items()
        if (routes := nonliteral_routes(source, path, slots))
    ]


def violations(root: Path = ROOT) -> list[str]:
    """Reject new routes and any changed source or dependency of a pinned route."""
    observed = {entry["source"]: entry for entry in inventory(root)}
    pin_path = root / PINS.relative_to(ROOT)
    pinned = json.loads(pin_path.read_text(encoding="utf8")) if pin_path.exists() else []
    errors = []
    for entry in pinned:
        actual = observed.pop(entry["source"], None)
        expected = {key: value for key, value in entry.items() if key != "reason"}
        if not entry.get("reason", "").strip() or actual != expected:
            errors.append("Changed/stale nonliteral route approval: " + entry["source"])
    errors.extend("Nonliteral transport route: " + path for path in observed)
    return errors
