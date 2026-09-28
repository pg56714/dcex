"""Every implemented ledger claim must have callable wrappers and wire-test evidence."""

import importlib
import json
import re
from functools import cache

import pytest

from tests.unit.ledger_route_evidence import (
    EXCHANGES,
    ROOT,
    route_evidence,
    route_key,
    wire_route_matches,
)

LEDGER = json.loads((ROOT / "docs/endpoint-coverage-ledger.json").read_text(encoding="utf-8"))
IMPLEMENTED = [r for r in LEDGER["rows"] if r["status"] == "implemented"]


@cache
def _python_methods(exchange: str, asynchronous: bool) -> set[str]:
    prefix = "dcex.async_support" if asynchronous else "dcex"
    modules = [importlib.import_module(f"{prefix}.{exchange}.client")]
    if exchange == "arcus":
        modules.append(importlib.import_module(f"{prefix}.arcus.spot"))
    return {
        name
        for module in modules
        for cls in vars(module).values()
        if isinstance(cls, type) and cls.__module__.startswith(f"{prefix}.{exchange}")
        for name in dir(cls)
        if callable(getattr(cls, name))
    }


@cache
def _rust_methods(exchange: str) -> set[str]:
    source = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (ROOT / "crates/dcex/src/exchanges" / exchange).rglob("*.rs")
        if "tests" not in p.parts and p.name != "tests.rs"
    )
    names = set(re.findall(r"\bfn\s+(\w+)\s*[<(]", source))
    for block in re.findall(r"impl_exchange_method_wrappers!\s*[({](.*?);\s*[)}]", source, re.S):
        names.update(re.findall(r"\b(\w+)\s*\(", block))
    for block in re.findall(
        r"(?:subaccount_query_methods|staking_methods)!\s*\((.*?)\)", source, re.S
    ):
        names.update(re.findall(r"\b\w+\b", block))
    return names


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_implemented_methods_exist_in_all_three_clients(exchange: str) -> None:
    """A ledger cannot retain deleted, misspelled or Python-only method names."""
    failures = []
    for row in IMPLEMENTED:
        if row["exchange"] != exchange:
            continue
        if not row["methods"]:
            failures.append(f"row {row['row']}: no methods")
        for method in row["methods"]:
            for asynchronous in (False, True):
                if method not in _python_methods(exchange, asynchronous):
                    failures.append(
                        f"row {row['row']}: {method} missing in Python async={asynchronous}"
                    )
            if method not in _rust_methods(exchange):
                failures.append(f"row {row['row']}: {method} missing in Rust wrappers")
    assert not failures, "\n".join(failures)


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_implemented_routes_match_executed_wire_cases(exchange: str) -> None:
    """Compare verb, path and action/tx type with the independent offline suites."""
    evidence = [e for e in route_evidence() if e.exchange == exchange]
    failures = []
    for row in IMPLEMENTED:
        if row["exchange"] != exchange:
            continue
        if not row.get("http_method") or not row.get("path"):
            failures.append(f"row {row['row']}: missing explicit HTTP method/path")
            continue
        selectors = row.get("actions", [str(tx) for tx in row.get("tx_types", [])])
        for name in row["methods"]:
            matches = [
                e
                for e in evidence
                if e.name == name
                and e.method == row["http_method"]
                and wire_route_matches(exchange, row["http_method"], row["path"], e.path)
                and (not selectors or e.selector in selectors)
            ]
            if not matches:
                failures.append(
                    f"row {row['row']}: {name} does not call {row['http_method']} {row['path']}"
                )
            for match in matches:
                assert (ROOT / match.evidence.split("::", 1)[0]).is_file(), match
    assert not failures, "\n".join(failures)


def test_ledger_counts_and_row_ids_are_consistent() -> None:
    """Summary counts cannot diverge from the endpoint rows shown in HTML."""
    from collections import Counter

    rows = LEDGER["rows"]
    assert len(rows) == LEDGER["row_count"]
    assert len({r["row"] for r in rows}) == len(rows)
    assert dict(Counter(r["status"] for r in rows)) == LEDGER["counts"]
    assert not any(r["status"] == "excluded" for r in rows)


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_official_inventory_has_a_ledger_disposition(exchange: str) -> None:
    """New official operations must be visible even before implementation."""
    inventory = json.loads(
        (ROOT / f"docs/official-endpoint-inventory/{exchange}.json").read_text(encoding="utf-8")
    )["endpoints"]
    rows = [r for r in LEDGER["rows"] if r["exchange"] == exchange]
    missing = []
    for endpoint in inventory:
        matches = [
            r
            for r in rows
            if r.get("http_method") == endpoint["method"].upper()
            and route_key(r.get("path", "")) == route_key(endpoint["path"])
            and r.get("host", endpoint.get("host")) == endpoint.get("host", r.get("host"))
            and r.get("channel") == endpoint.get("channel")
            and r.get("operation") == endpoint.get("operation")
            and (not endpoint.get("action") or endpoint["action"] in r.get("actions", []))
        ]
        if not matches:
            missing.append(f"{endpoint['method']} {endpoint['path']} {endpoint.get('action', '')}")
    assert not missing, "\n".join(missing)


@pytest.mark.parametrize(
    ("exchange", "method", "template", "literal"),
    [
        ("kucoin", "GET", "/api/v1/accounts/{accountId}", "/api/v1/accounts/ledgers"),
        ("ondo", "GET", "/v1/perps/orders/{orderID}", "/v1/perps/orders/csv"),
        (
            "kraken",
            "GET",
            "/derivatives/api/v3/rfqs/{rfqUid}",
            "/derivatives/api/v3/rfqs/open-offers",
        ),
    ],
)
def test_reserved_paths_are_not_resource_ids(
    exchange: str, method: str, template: str, literal: str
) -> None:
    """A passing list/export test is not evidence for the resource-detail endpoint."""
    assert not wire_route_matches(exchange, method, template, literal)
