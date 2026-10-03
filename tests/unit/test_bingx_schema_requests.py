"""Exercise every additional BingX request against its official request table."""

import hashlib
import hmac
import importlib
import inspect
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import pytest

from scripts.build_bingx_wrappers import field_kind, operation_name
from scripts.build_bitget_wrappers import snake
from tests.unit.endpoint_wrapper_helpers import generated_method_members
from tests.unit.native_http_helpers import _http_server

ROOT = Path(__file__).resolve().parents[2]
OPERATIONS = json.loads(
    (ROOT / "docs/official-endpoint-inventory/sources/bingx-operations.json").read_text(
        encoding="utf8"
    )
)
NAMES = {operation_name(o) for o in OPERATIONS}


def fields(op):
    result = {}
    for f in op["parameters"]:
        key = f["name"]
        if key == "timestamp":
            continue
        value = op["example"].get(key)
        if value == "":
            value = None
        kind = field_kind(f)
        if kind == "int":
            value = int(value) if value is not None else 1
        elif kind == "decimal":
            value = str(value) if value is not None else "1"
        elif kind == "array":
            value = value or ["FUND"]
        elif kind == "bool":
            value = True
        else:
            value = str(value) if value is not None else "1"
        result[key] = value
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("op", OPERATIONS, ids=operation_name)
async def test_inventory_wire(asynchronous, op):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(prefix + ".bingx.client").Client
    values = fields(op)
    lindorm = op["path"].startswith("/api/lindorm/")
    if lindorm:
        values.update(access_token="platform-token", proxy_user="platform-user")
    with _http_server({"code": 0, "data": {}}) as (base, received):
        client = cls(
            api_key=None if lindorm else "key",
            api_secret=None if lindorm else "secret",
            base_url=base,
            preload_product_table=False,
        )
        if asynchronous:
            await client.async_init()
        try:
            result = getattr(client, operation_name(op))(**{snake(k): v for k, v in values.items()})
            if inspect.isawaitable(result):
                await result
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        assert received.qsize() == 1
        request = received.get_nowait()
    assert request["method"] == op["method"]
    assert urlsplit(request["path"]).path == op["path"]
    if lindorm:
        assert not urlsplit(request["path"]).query
        assert request["access_token"] == values.pop("access_token")
        assert request["proxy_user"] == values.pop("proxy_user")
        assert "bingx_api_key" not in request
        assert json.loads(request["body"]) == values
        return
    assert request["body"] == ""
    params = dict(parse_qsl(urlsplit(request["path"]).query))
    if op["signed"]:
        signature = params.pop("signature")
        preimage = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        assert signature == hmac.new(b"secret", preimage.encode(), hashlib.sha256).hexdigest()
        assert params.pop("timestamp").isdigit()
        assert request["bingx_api_key"] == "key"
    else:
        assert "bingx_api_key" not in request
    expected = {
        k: (json.dumps(v, separators=(",", ":")) if isinstance(v, (list, dict, bool)) else str(v))
        for k, v in values.items()
    }
    assert params == expected


def test_inventory_surface():
    for prefix in ["dcex", "dcex.async_support"]:
        cls = importlib.import_module(prefix + ".bingx._generated").GeneratedHTTP
        assert {k for k, v in generated_method_members(cls).items() if not k.startswith("_") and callable(v)} == NAMES
