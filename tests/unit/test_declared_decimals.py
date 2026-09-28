"""Every declared decimal is checked, including nested and websocket inputs."""

import ast
from decimal import Decimal
import json
from pathlib import Path
import re

import pytest

from dcex._input_codec import CATALOG, normalize, resolve_schema


def decimal_fields(schema, path=()):
    schema = resolve_schema(schema)
    if schema.get("format") == "decimal":
        yield path, schema
    for name, child in schema.get("properties", {}).items():
        yield from decimal_fields(child, (*path, name))
    if "items" in schema:
        yield from decimal_fields(schema["items"], (*path, "[]"))


FIELDS = [
    (f"{protocol}/{exchange}/{method}/{'/'.join(path)}", schema)
    for protocol in ("exchanges", "websocket")
    for exchange, methods in CATALOG[protocol].items()
    for method, contract in methods.items()
    for path, schema in decimal_fields(contract)
]


@pytest.mark.parametrize("name,schema", FIELDS, ids=[name for name, _ in FIELDS])
def test_every_declared_decimal_rejects_lossy_inputs(name, schema):
    assert normalize(Decimal("0.125000000000000001"), name, schema=schema) == "0.125000000000000001"
    for value in [0.1, 1e-7, True, "1e-7", "+1e-7", "NaN", "abc", " 1", "1 ", ".1"]:
        with pytest.raises(ValueError):
            normalize(value, name, schema=schema)
    if not schema.get("x-signed") and not schema.get("x-relative"):
        with pytest.raises(ValueError):
            normalize("-3", name, schema=schema)


def test_catalog_is_identical_in_python_and_rust():
    root = Path(__file__).resolve().parents[2]
    assert CATALOG == json.loads((root / "crates/dcex/src/exchanges/input_contracts.json").read_text(encoding="utf-8"))


def test_existing_explicit_decimal_fields_have_input_declarations():
    root = Path(__file__).resolve().parents[2] / "crates/dcex/src/exchanges"
    missing = []
    for path in root.glob("*/schemas/*.json"):
        exchange = path.parent.parent.name
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        for row in rows:
            contract = CATALOG["exchanges"].get(exchange, {}).get(row.get("name"), {})
            if contract:
                assert row["input_schema"] == contract
            for field in row.get("fields", []):
                if not isinstance(field, dict):
                    continue
                if field.get("kind", field.get("type")) not in {"decimal", "positive", "d"} and field.get("format") != "decimal":
                    continue
                name = field.get("wire", field.get("name", field.get("key")))
                if contract.get("properties", {}).get(name, {}).get("format") != "decimal":
                    missing.append((exchange, row["name"], name))
    assert not missing


def test_boolean_parameters_are_not_declared_decimal():
    root = Path(__file__).resolve().parents[2] / "dcex"
    conflicts = []
    for exchange, methods in CATALOG["exchanges"].items():
        for path in (root / exchange).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name not in methods:
                    continue
                booleans = {
                    arg.arg.replace("_", "").lower()
                    for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
                    if arg.annotation is not None and any(
                        isinstance(part, ast.Name) and part.id == "bool"
                        for part in ast.walk(arg.annotation)
                    )
                }
                for name, field in methods[node.name].get("properties", {}).items():
                    if name.replace("_", "").lower() in booleans and field.get("format") == "decimal":
                        conflicts.append((exchange, node.name, name))
    assert not conflicts


def test_undeclared_field_names_do_not_imply_financial_semantics():
    assert normalize({"price": "label", "amount": 0.5}) == {"price": "label", "amount": 0.5}


def test_every_native_dispatch_validates_its_explicit_endpoint():
    root = Path(__file__).resolve().parents[2] / "crates/dcex/src/exchanges"
    seen = []
    pattern = r"pub async fn (?:private_request|public_request)\(.*?\) -> Result<ValidatedResponse> \{\s*([^\n]+)"
    for path in root.glob("*/*.rs"):
        for match in re.finditer(pattern, path.read_text(encoding="utf-8"), re.S):
            assert f'input_contracts::pairs("{path.parent.name}", method_name, &params)?;' in match[1], path
            seen.append(path.parent.name)
    assert len(seen) == 32  # Fifteen perpetual/default clients plus Arcus spot.


def test_relative_prices_are_scoped_to_kraken():
    for value in ["+5", "-5", "#5", "+5.25%", "-5%", "#5.5%"]:
        for method, key in [("place_spot_order", "price"), ("amend_spot_order", "limit_price"), ("amend_spot_order", "trigger_price")]:
            normalize({key: value}, schema=CATALOG["exchanges"]["kraken"][method])
        for exchange in ["binance", "bybit", "backpack"]:
            with pytest.raises(ValueError):
                normalize({"price": value}, schema=CATALOG["exchanges"][exchange]["place_order"])


def test_nested_json_scientific_spelling_is_not_rounded_away():
    schema = CATALOG["exchanges"]["bingx"]["place_coin_swap_order"]
    with pytest.raises(ValueError):
        normalize({"takeProfit": '{"price":1e-7}'}, schema=schema)
