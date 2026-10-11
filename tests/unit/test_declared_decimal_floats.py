"""Every public wrapper rejects a float for each declared decimal before building a body."""

import importlib
import inspect

import pytest

from dcex import _input_codec as declared

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
