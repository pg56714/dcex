"""Canonical keyword compatibility must preserve wire data and async semantics."""

import inspect
import json
from importlib import import_module
from pathlib import Path

import pytest

from dcex._keyword_aliases import legacy_keywords

ALIASES = json.loads(
    (Path(__file__).parents[1] / "fixtures/keyword_aliases.json").read_text(encoding="utf-8")
)


@pytest.mark.parametrize("case", ALIASES, ids=lambda c: c["file"] + ":" + c["method"])
def test_canonical_signature_and_legacy_metadata(case):
    module = case["file"].replace("\\", ".").replace("/", ".").removesuffix(".py")
    cls = import_module(module).TradeHTTP
    method = getattr(cls, case["method"])
    params = inspect.signature(method).parameters
    assert all(new in params and old not in params for old, new in case["aliases"].items())
    assert method.__legacy_keywords__ == case["aliases"]
    assert inspect.iscoroutinefunction(method) == ("async_support" in module)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.asyncio
async def test_aliases_preserve_payload_and_reject_conflicts(asynchronous):
    captured = []

    def sync(*, order_id):
        captured.append(order_id)
        return order_id

    async def async_(*, order_id):
        return sync(order_id=order_id)

    fn = legacy_keywords({"orderId": "order_id"})(async_ if asynchronous else sync)
    for kwargs in ({"orderId": "123"}, {"order_id": "123"}):
        result = fn(**kwargs)
        if asynchronous:
            result = await result
        assert result == "123"
    with pytest.raises(TypeError, match="legacy alias"):
        result = fn(orderId="old", order_id="new")
        if asynchronous:
            await result
    assert captured == ["123", "123"]
