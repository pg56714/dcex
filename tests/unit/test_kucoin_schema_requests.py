"""Independent official request tables verify KuCoin host, body and both signatures."""

import base64
import hashlib
import hmac
import importlib
import inspect
import json
from contextlib import ExitStack
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit

import pytest

from scripts.build_bitget_wrappers import snake
from scripts.build_kucoin_wrappers import operation_name
from tests.unit.endpoint_wrapper_helpers import generated_method_members
from tests.unit.native_http_helpers import _http_server
from tests.unit.test_bitget_schema_requests import sample

ROOT = Path(__file__).resolve().parents[2]
OPERATIONS = json.loads(
    (ROOT / "docs/official-endpoint-inventory/sources/kucoin-operations.json").read_text(
        encoding="utf-8"
    )
)
NAMES = {operation_name(op) for op in OPERATIONS}


def values_for(op):
    query = {}
    path = op["path"]
    kwargs = {}
    for location in ("path", "query"):
        for field in op["parameters"][location]:
            schema = field.get("schema") or {"type": field["type"]}
            value = sample(schema)
            if schema.get("type") == "number":
                value = str(value)
            kwargs[snake(field["name"])] = value
            if location == "path":
                path = path.replace("{" + field["name"] + "}", str(value))
            else:
                query[field["name"]] = str(value)
    schema = op["requestBody"].get("jsonSchema", {})
    body = None
    if op["requestBody"]["type"] == "application/json":
        if "$ref" in schema:
            raw = op["requestBody"]["examples"][0]["value"]
            body, _ = json.JSONDecoder().raw_decode(raw[raw.index("{") :])
            kwargs["body"] = body
        else:
            body = sample(schema)
            for key, spec in schema["properties"].items():
                if spec.get("type") == "number":
                    body[key] = str(body[key])
            kwargs.update({snake(k): v for k, v in body.items()})
    if op["method"] == "delete" and "apikey" in path:
        kwargs["confirm"] = True
    return kwargs, path, query, body


def signature(secret, preimage):
    return base64.b64encode(
        hmac.new(secret.encode(), preimage.encode(), hashlib.sha256).digest()
    ).decode()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("op", OPERATIONS, ids=operation_name)
async def test_inventory_wire(asynchronous, op):
    cls = importlib.import_module(
        ("dcex.async_support" if asynchronous else "dcex") + ".kucoin.client"
    ).Client
    kwargs, path, query, body = values_for(op)
    with ExitStack() as stack:
        servers = {
            market: stack.enter_context(_http_server({"code": "200000", "data": {}}))
            for market in ("spot", "futures", "broker")
        }
        client = cls(
            api_key="key",
            api_secret="secret",
            passphrase="passphrase",
            preload_product_table=False,
            base_url=servers["spot"][0],
            futures_base_url=servers["futures"][0],
            broker_base_url=servers["broker"][0],
            broker_partner="partner",
            broker_key="broker-secret",
            broker_name="broker-name",
        )
        if asynchronous:
            await client.async_init()
        try:
            result = getattr(client, operation_name(op))(**kwargs)
            if inspect.isawaitable(result):
                await result
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        market = op["customApiFields"]["10"].lower()
        for name, (_, received) in servers.items():
            assert received.qsize() == (1 if name == market else 0)
        request = servers[market][1].get_nowait()
    assert request["method"] == op["method"].upper()
    assert urlsplit(request["path"]).path == path
    assert dict(parse_qsl(urlsplit(request["path"]).query)) == query
    assert (json.loads(request["body"]) if request["body"] else None) == body
    timestamp = request["KC-API-TIMESTAMP"]
    assert timestamp.isdigit()
    assert request["KC-API-SIGN"] == signature(
        "secret", timestamp + request["method"] + unquote(request["path"]) + request["body"]
    )
    assert request["KC-API-KEY"] == "key"
    assert request["KC-API-PASSPHRASE"] == signature("secret", "passphrase")
    assert request["KC-API-KEY-VERSION"] == "2"
    assert request["KC-API-PARTNER-SIGN"] == signature(
        "broker-secret", timestamp + "partner" + "key"
    )
    assert request["KC-API-PARTNER"] == "partner"
    assert request["KC-BROKER-NAME"] == "broker-name"
    assert request["KC-API-PARTNER-VERIFY"] == "true"


def test_inventory_surface():
    assert len(NAMES) == len(OPERATIONS)
    for prefix in ("dcex", "dcex.async_support"):
        cls = importlib.import_module(prefix + ".kucoin._generated").GeneratedHTTP
        assert {
            name
            for name, method in generated_method_members(cls).items()
            if not name.startswith("_") and callable(method)
        } == NAMES
