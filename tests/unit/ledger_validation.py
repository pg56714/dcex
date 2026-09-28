"""Independent validation of ledger replacement chains and evidence symbols."""

import ast
import re
from functools import cache
from pathlib import Path
from urllib.parse import urlsplit

ROUTE_FIELDS = ("exchange", "http_method", "path", "host", "channel", "actions", "tx_types", "operation")


def route_identity(row):
    return {key: row.get(key) for key in ROUTE_FIELDS}


def validate_superseded(rows, replacements):
    by_id = {row["row"]: row for row in rows}

    def visit(number, ancestors):
        assert number in by_id, (number, "missing target")
        assert number not in ancestors, (number, "replacement cycle")
        row = by_id[number]
        if row["status"] in {"implemented", "protocol"}:
            return
        assert row["status"] == "superseded", (number, "inactive target")
        targets = row.get("superseded_by")
        assert targets, (number, "replacement chain has no active destination")
        for target_id in targets if isinstance(targets, list) else [targets]:
            assert target_id in by_id, (number, target_id, "missing target")
            target = by_id[target_id]
            assert row["exchange"] == target["exchange"], (number, target_id)
            same = route_identity(row) == route_identity(target)
            grouped = row.get("channel") is not None and row["channel"] in target.get("channels", [])
            grouped = grouped or any(
                all(row.get(key) == value for key, value in route.items())
                for route in target.get("covered_routes", [])
            )
            declared = any(
                entry["source"] == route_identity(row)
                and route_identity(target) in entry["targets"]
                for entry in replacements
            )
            assert same or grouped or declared, (number, target_id, "undeclared replacement")
            visit(target_id, {*ancestors, number})

    for row in rows:
        if row["status"] != "superseded":
            continue
        if not row.get("superseded_by"):
            reason = row.get("superseded_reason", "")
            assert isinstance(reason, str) and len(reason.strip()) >= 20 and len(set(re.findall(r"[A-Za-z]{2,}", reason.lower()))) >= 4, (row["row"], "missing reason")
        else:
            visit(row["row"], set())


@cache
def python_symbols(source):
    paths = set()

    def walk(nodes, prefix=""):
        for node in nodes:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                path = prefix + node.name
                paths.add(path)
                walk(node.body, path + ".")

    walk(ast.parse(source).body)
    return paths


@cache
def rust_symbols(source):
    # Ignore comments and quoted content before recognizing actual declarations.
    tokens = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|r(?P<hash>\#*)"[\s\S]*?"(?P=hash)|"(?:\\[\s\S]|[^"\\])*"')
    # A char literal containing a double quote must not start a string token.
    chars = re.compile(r"'(?:\\.|[^'\\\n])'")
    code = tokens.sub(" ", chars.sub(" ", source))
    return set(re.findall(r"\b(?:fn|struct|enum|trait|type|const|static|mod)\s+(\w+)", code))


def validate_evidence(root: Path, evidence: str):
    if evidence.startswith(("https://", "http://")):
        assert urlsplit(evidence).hostname, evidence
        return
    assert not re.search(r":\d+$", evidence), evidence
    path, separator, symbol = evidence.partition("::")
    target = root / path
    assert target.exists(), evidence
    if not separator:
        return
    assert target.is_file(), evidence
    source = target.read_text(encoding="utf-8")
    if target.suffix == ".py":
        assert symbol in python_symbols(source), evidence
    elif target.suffix == ".rs":
        assert symbol in rust_symbols(source), evidence
    else:
        raise AssertionError(f"Unsupported evidence symbol file: {evidence}")
