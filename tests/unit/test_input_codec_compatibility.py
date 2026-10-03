"""Verify the new codec's call compatibility before switching existing users."""

import ast
import importlib
import inspect
from decimal import Decimal
from enum import Enum
from pathlib import Path

import pytest

from dcex import _input_codec as declared
from dcex import _schema_codec as compatibility


class Example(Enum):
    ONE = "1"


@pytest.mark.parametrize("values", [
    {"quantity": Decimal("0.1234567890123456789"), "price": "1.25"},
    {"orders": [{"price": "2", "quantity": 3}], "enabled": True, "ids": (1, 2)},
    {"amount": "-3", "size": "", "price": "+5", "tpOrdPx": "-1"},
    {"quantity": Example.ONE, "optional": None, "timeout": 0.5},
    {"payload": '{"price":0.125000000000000001}'},
])
def test_legacy_serializer_call_shapes_keep_exact_values(values):
    import json
    def expected(value):
        if isinstance(value, Decimal):
            return format(value, "f")
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {key: expected(child) for key, child in value.items()}
        if isinstance(value, (tuple, list)):
            return [expected(child) for child in value]
        return value
    assert compatibility.normalize_params(values) == expected(values)
    assert compatibility.encode_json(values, separators=(",", ":"), ensure_ascii=False) == json.dumps(expected(values), separators=(",", ":"), ensure_ascii=False)


def test_signed_fields_interface_remains_accepted():
    body = {"legs": [{"size": Decimal("-0.25")}]}
    assert compatibility.encode_json(body, signed_fields=("size",), allow_nan=False) == '{"legs": [{"size": "-0.25"}]}'


def test_every_existing_imported_codec_call_has_compatible_signature():
    for path in (Path(__file__).resolve().parents[2] / "dcex").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {alias.asname or alias.name: alias.name for node in ast.walk(tree)
                   if isinstance(node, ast.ImportFrom) and (node.module or "").endswith("_schema_codec")
                   for alias in node.names}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id not in imports:
                continue
            signature = inspect.signature(getattr(declared, imports[node.func.id]))
            args = [object() for arg in node.args if not isinstance(arg, ast.Starred)]
            kwargs = {kw.arg: object() for kw in node.keywords if kw.arg is not None}
            signature.bind_partial(*args, **kwargs)


CASES = [
    (exchange, method, name, schema)
    for exchange, methods in declared.CATALOG["exchanges"].items()
    for method, schema in methods.items()
    for name, field in schema["properties"].items()
    if field.get("format") == "decimal"
]


@pytest.mark.parametrize("exchange,method,name,schema", CASES)
def test_actual_public_method_can_reject_each_declared_float_before_body(exchange, method, name, schema):
    cls = importlib.import_module(f"dcex.{exchange}.client").Client
    function = getattr(cls, method, None)
    if function is None:
        # Native-only names have their own exhaustive Rust catalog walk.
        return
    assert hasattr(function, "__wrapped__"), (exchange, method)
    assert inspect.signature(function) == inspect.signature(function.__wrapped__)
    with pytest.raises(ValueError, match="exact decimal"):
        function(object(), **{name: 1e-7})
