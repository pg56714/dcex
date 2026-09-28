"""Exercise additional V5 routes against independent official HTTP examples."""

import hashlib
import hmac
import inspect
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_bybit_endpoint_coverage import _native_client

CASES = json.loads(
    (Path(__file__).parents[1] / "fixtures/bybit_request_cases.json").read_text(encoding="utf-8")
)["cases"]


def wire_string(value):
    if isinstance(value, (bool, list, dict)):
        return json.dumps(value, separators=(",", ":"))
    return str(value)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
async def test_full_official_request_and_signature(case, asynchronous):
    from dcex.async_support.bybit.client import Client as AsyncClient
    from dcex.bybit.client import Client

    with _http_server({"retCode": 0, "retMsg": "OK", "result": {}}) as (base, received):
        client = (AsyncClient if asynchronous else Client)(
            api_key="api-key",
            api_secret="api-secret",
            sync_server_time=False,
            preload_product_table=False,
        )
        if asynchronous:
            await client.async_init()
        client._native_client = _native_client(base)
        try:
            result = getattr(client, case["name"])(**case["kwargs"])
            if inspect.isawaitable(result):
                await result
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        request = received.get(timeout=2)
        assert received.empty()
    url = urlsplit(request["path"])
    assert (request["method"], url.path) == (case["method"], case["path"])
    if case["method"] == "GET":
        assert request["body"] == ""
        assert dict(parse_qsl(url.query)) == {k: wire_string(v) for k, v in case["wire"].items()}
        payload = url.query
    else:
        assert url.query == ""
        assert json.loads(request["body"]) == case["wire"]
        payload = request["body"]
    if case["signed"]:
        assert request["X-BAPI-API-KEY"] == "api-key"
        preimage = request["X-BAPI-TIMESTAMP"] + "api-key" + request["X-BAPI-RECV-WINDOW"] + payload
        assert (
            request["X-BAPI-SIGN"]
            == hmac.new(
                b"api-secret",
                preimage.encode(),
                hashlib.sha256,
            ).hexdigest()
        )
    else:
        assert "X-BAPI-SIGN" not in request
        assert "X-BAPI-API-KEY" not in request


@pytest.mark.parametrize(
    "name,params,error",
    [
        (
            "create_withdrawal",
            {
                "coin": "USDT",
                "address": "test",
                "amount": "1",
                "timestamp": "1",
                "accountType": "FUND",
            },
            "chain is required",
        ),
        ("submit_event_quote", {"symbol": "ETH", "amount": "1"}, "orderLinkId.*required"),
        (
            "set_mmp_config",
            {
                "baseCoin": "BTC",
                "window": "1",
                "frozenPeriod": "1",
                "qtyLimit": "1",
                "deltaLimit": "1",
                "unknown": "x",
            },
            "unknown parameter",
        ),
        (
            "request_grid_validate_input",
            {"symbol": "BTCUSDT", "cell_number": "1.5", "min_price": "1", "max_price": "2"},
            "integer",
        ),
    ],
)
def test_invalid_request_rejected_without_transport(name, params, error):
    client = _native_client("http://127.0.0.1:1")
    public = name == "request_grid_validate_input"
    with pytest.raises(ValueError, match=error):
        getattr(client, "public_request_json" if public else "private_request_json")(
            name, list(params.items())
        )
