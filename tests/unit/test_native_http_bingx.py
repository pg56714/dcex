"""Offline coverage for native http bingx."""
# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_bingx_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.BingxHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=10,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "GET",
            "/test",
            [("symbol", "BTC USDT"), ("limit", "10"), ("type", "LIMIT")],
            True,
        )

    request = received.get_nowait()
    pairs = parse_qsl(urlsplit(request["path"]).query)
    signed_pairs = pairs[:-1]
    signature = pairs[-1][1]
    payload = "&".join(f"{key}={value}" for key, value in signed_pairs)
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert body == {"ok": True}
    assert request["bingx_api_key"] == "api-key"
    assert signed_pairs[0] == ("limit", "10")
    assert signed_pairs[1] == ("symbol", "BTC USDT")
    assert signed_pairs[2][0] == "timestamp"
    assert signed_pairs[3] == ("type", "LIMIT")
    assert pairs[-1][0] == "signature"
    assert signature == expected_signature


def test_native_bingx_listen_key_requires_api_key() -> None:
    native = pytest.importorskip("dcex._native")

    client = native.BingxHttpClient(timeout=2)
    with pytest.raises(ValueError, match="BingX API key is required for this request"):
        client.private_request_json("get_listen_key")


def test_sync_bingx_listen_key_uses_api_key_without_secret() -> None:
    from dcex.bingx.client import Client

    with _http_server({"code": 0, "listenKey": "listen-key"}) as (base_url, received):
        client = Client(
            api_key="api-key",
            base_url=base_url,
            preload_product_table=False,
        )
        result = client.get_listen_key()

    client.close()
    request = received.get_nowait()
    assert result == "listen-key"
    assert request["bingx_api_key"] == "api-key"


@pytest.mark.asyncio
async def test_async_bingx_listen_key_uses_api_key_without_secret() -> None:
    from dcex.async_support.bingx.client import Client

    with _http_server({"code": 0, "listenKey": "listen-key"}) as (base_url, received):
        client = Client(
            api_key="api-key",
            base_url=base_url,
            preload_product_table=False,
        )
        await client.async_init()
        result = await client.get_listen_key()

    await client.close()
    request = received.get_nowait()
    assert result == "listen-key"
    assert request["bingx_api_key"] == "api-key"


def test_sync_bingx_manager_uses_native_transport() -> None:
    from dcex.bingx._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/test",
            {"symbol": "BTCUSDT"},
            signed=False,
        )

    manager.close()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=BTCUSDT"


def test_sync_bingx_manager_sends_unsigned_json_body() -> None:
    from dcex.bingx._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "POST",
            "/test",
            {"symbol": "BTCUSDT", "limit": 1},
            signed=False,
        )

    manager.close()
    request = received.get_nowait()
    assert result == {"ok": True}
    assert request["path"] == "/test"
    assert request["body"] == '{"symbol":"BTCUSDT","limit":1}'


@pytest.mark.asyncio
async def test_async_bingx_manager_uses_native_transport() -> None:
    from dcex.async_support.bingx._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/test",
            {"symbol": "ETHUSDT"},
            signed=False,
        )

    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=ETHUSDT"


def test_sync_bingx_public_wrapper_uses_native_dispatcher() -> None:
    from dcex.bingx.client import Client

    with _http_server({"code": 0, "data": []}) as (base_url, received):
        client = Client(base_url=base_url, preload_product_table=False)
        result = client.get_orderbook("BTC-USDT", limit=5)

    client.close()
    assert result == {"code": 0, "data": []}
    assert client.last_response_headers["x-response"] == "native"
    # BingX also requires a timestamp here; its value varies, so compare the stable prefix.
    assert received.get_nowait()["path"].startswith(
        "/openApi/swap/v2/quote/depth?limit=5&symbol=BTC-USDT"
    )


@pytest.mark.asyncio
async def test_async_bingx_public_wrapper_uses_native_dispatcher() -> None:
    from dcex.async_support.bingx.client import Client

    with _http_server({"code": 0, "data": []}) as (base_url, received):
        client = Client(base_url=base_url, preload_product_table=False)
        await client.async_init()
        result = await client.get_spot_orderbook_v2(
            "ETH-USDT-SPOT",
            depth=10,
            type_="step1",
        )

    await client.close()
    assert result == {"code": 0, "data": []}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == (
        "/openApi/spot/v2/market/depth?depth=10&symbol=ETH_USDT&type=step1"
    )


def test_native_bingx_private_spot_order_uses_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": 0, "data": {"orderId": "1"}}) as (base_url, received):
        client = native.BingxHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=10,
            base_url=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_spot_limit_buy_order",
            [
                ("product_symbol", "BTC-USDT-SPOT"),
                ("quantity", "0.001"),
                ("price", "100"),
            ],
        )

    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    assert status == 200
    assert body == {"code": 0, "data": {"orderId": "1"}}
    assert urlsplit(request["path"]).path == "/openApi/spot/v1/trade/order"
    assert request["bingx_api_key"] == "api-key"
    assert query["symbol"] == "BTC-USDT"
    assert query["side"] == "BUY"
    assert query["type"] == "LIMIT"
    assert query["quantity"] == "0.001"
    assert query["price"] == "100"
    assert "timestamp" in query
    assert "signature" in query


def test_native_bingx_private_batch_order_normalizes_numbers() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": 0, "data": {"orders": []}}) as (base_url, received):
        client = native.BingxHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=10,
            base_url=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_swap_batch_order",
            [
                (
                    "batchOrders",
                    json.dumps(
                        [
                            {
                                "symbol": "BTC-USDT",
                                "side": "BUY",
                                "type": "LIMIT",
                                "quantity": "0.001",
                                "price": "100",
                            }
                        ],
                        separators=(",", ":"),
                    ),
                )
            ],
        )

    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    orders = json.loads(query["batchOrders"])
    assert status == 200
    assert body == {"code": 0, "data": {"orders": []}}
    assert urlsplit(request["path"]).path == "/openApi/swap/v2/trade/batchOrders"
    assert orders[0]["quantity"] == 0.001
    assert orders[0]["price"] == 100
    assert "signature" in query


@pytest.mark.asyncio
async def test_async_bingx_manager_sends_unsigned_json_body() -> None:
    from dcex.async_support.bingx.client import Client

    with _http_server() as (base_url, received):
        manager = Client(base_url=base_url, preload_product_table=False)
        try:
            await manager.async_init()
            result = await manager._request(
                "POST", "/test", {"symbol": "BTCUSDT", "limit": 1}, signed=False
            )
        finally:
            await manager.close()
    request = received.get_nowait()
    assert result == {"ok": True}
    assert request["path"] == "/test"
    assert request["body"] == '{"symbol":"BTCUSDT","limit":1}'
    assert "bingx_api_key" not in request
