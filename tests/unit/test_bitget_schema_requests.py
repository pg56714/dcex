"""Compare additional Bitget wrappers with the committed official operation schemas."""

import base64
import hashlib
import hmac
import importlib
import inspect
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import pytest
from tests.unit.endpoint_wrapper_helpers import generated_method_members

from scripts.build_bitget_wrappers import snake
from scripts.wrapper_codegen import load_schemas
from tests.unit.native_http_helpers import _http_server

ROOT = Path(__file__).resolve().parents[2]
SPECS = load_schemas("bitget")
NAMES = {s["name"] for s in SPECS}
OPERATIONS = [
    op
    for op in json.loads(
        (ROOT / "docs/official-endpoint-inventory/sources/bitget-operations.json").read_text(
            encoding="utf-8"
        )
    )["operations"]
    if snake(op["operationId"]) in NAMES
]


def sample(schema):
    if schema.get("enum"):
        return schema["enum"][0]
    if "example" in schema:
        return schema["example"]
    if schema.get("examples"):
        return schema["examples"][0]
    kind = schema.get("type", "string")
    if kind == "object":
        return {key: sample(value) for key, value in schema.get("properties", {}).items()}
    if kind == "array":
        return [sample(schema.get("items", {}))]
    if kind == "boolean":
        return True
    if kind in {"integer", "number"}:
        return max(1, schema.get("minimum", 1))
    return "1"


def case(op):
    query = {p["name"]: sample(p["schema"]) for p in op["parameters"] if p["in"] == "query"}
    content = (op.get("requestBody") or {}).get("content", [])
    body = sample(content[0]["schema"]) if content else None
    values = {**query, **(body or {})}
    kwargs = {snake(key): value for key, value in values.items()}
    name = snake(op["operationId"])
    signature = inspect.signature(
        getattr(importlib.import_module("dcex.bitget.client").Client, name)
    )
    if "confirm" in signature.parameters:
        kwargs["confirm"] = True
    return name, kwargs, query, body


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("op", OPERATIONS, ids=lambda op: op["operationId"])
async def test_inventory_wire(asynchronous, op):
    from tests.unit.test_bitget_endpoint_coverage import _client_kwargs

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.bitget.client").Client
    name, kwargs, query, body = case(op)
    description = op.get("description") or ""
    public = (
        op["method"] == "get"
        and ("/market/" in op["path"] or "/public/" in op["path"])
        and "(IP)" in description
    )
    with _http_server({"code": "00000", "data": {}}) as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            result = getattr(client, name)(**kwargs)
            if inspect.isawaitable(result):
                await result
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        assert received.qsize() == 1
        request = received.get_nowait()
    assert request["method"] == op["method"].upper()
    assert urlsplit(request["path"]).path == op["path"]
    actual = dict(parse_qsl(urlsplit(request["path"]).query))
    expected = {
        key: (json.dumps(value, separators=(",", ":")) if not isinstance(value, str) else value)
        for key, value in query.items()
    }
    assert actual == expected
    assert (json.loads(request["body"]) if request["body"] else None) == body
    if public:
        assert "ACCESS-SIGN" not in request
    else:
        preimage = (
            request["ACCESS-TIMESTAMP"] + request["method"] + request["path"] + request["body"]
        )
        expected_signature = base64.b64encode(
            hmac.new(b"api-secret", preimage.encode(), hashlib.sha256).digest()
        ).decode()
        assert request["ACCESS-SIGN"] == expected_signature
        assert request["ACCESS-KEY"] == "api-key"


def test_inventory_surface_is_fully_exercised():
    assert len(OPERATIONS) == len(NAMES)
    for prefix in ("dcex", "dcex.async_support"):
        cls = importlib.import_module(f"{prefix}.bitget._generated").GeneratedHTTP
        assert {
            name
            for name, value in generated_method_members(cls).items()
            if callable(value) and not name.startswith("_")
        } == NAMES
