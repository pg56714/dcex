# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def _next_non_binance_time_request(received) -> dict[str, Any]:  # noqa: ANN001
    while True:
        request = received.get_nowait()
        path = urlsplit(request["path"]).path
        if path not in {"/api/v3/time", "/fapi/v1/time"}:
            return request


def test_native_sync_http_client() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.HttpClient(timeout=2)
        status, headers, body = client.request(
            "GET",
            base_url,
            "/test",
            [("symbol", "BTCUSDT")],
            {"X-Test": "sync"},
        )

    assert status == 200
    assert headers["x-response"] == "native"
    assert json.loads(body) == {"ok": True}
    assert received.get_nowait() == {
        "path": "/test?symbol=BTCUSDT",
        "header": "sync",
        "api_key": None,
    }


@pytest.mark.asyncio
async def test_native_async_http_client() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.HttpClient(timeout=2)
        status, headers, body = await client.request_async(
            "GET",
            base_url,
            "/test",
            [("symbol", "ETHUSDT")],
            {"X-Test": "async"},
        )

    assert status == 200
    assert headers["x-response"] == "native"
    assert json.loads(body) == {"ok": True}
    assert received.get_nowait() == {
        "path": "/test?symbol=ETHUSDT",
        "header": "async",
        "api_key": None,
    }


def test_native_binance_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request(
            "GET",
            "spot",
            "/test",
            [("symbol", "BTCUSDT")],
            True,
        )

    request = _next_non_binance_time_request(received)
    signed_query, signature = request["path"].split("?", 1)[1].rsplit("&signature=", 1)
    expected_signature = hmac.new(
        b"secret",
        signed_query.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert request["api_key"] == "api-key"
    assert "timestamp=" in signed_query
    assert "recvWindow=5000" in signed_query
    assert signature == expected_signature


@pytest.mark.asyncio
async def test_native_binance_async_public_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = await client.request_async(
            "GET",
            "futures",
            "/test",
            [("symbol", "ETHUSDT")],
            False,
        )

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert received.get_nowait()["path"] == "/test?symbol=ETHUSDT"


def test_sync_binance_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.binance._http_manager import HTTPManager
    from dcex.binance.endpoints.market import SpotMarket

    with _http_server() as (base_url, received):
        manager = HTTPManager(preload_product_table=False)
        manager._native_client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = manager._request(
            "GET",
            SpotMarket.EXCHANGE_INFO,
            {"symbol": "BTCUSDT"},
            signed=False,
        )

    manager.close()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == (f"{SpotMarket.EXCHANGE_INFO}?symbol=BTCUSDT")


@pytest.mark.asyncio
async def test_async_binance_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.binance._http_manager import HTTPManager
    from dcex.async_support.binance.endpoints.market import SpotMarket

    with _http_server() as (base_url, received):
        manager = HTTPManager(preload_product_table=False)
        await manager.async_init()
        manager._native_client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = await manager._request(
            "GET",
            SpotMarket.EXCHANGE_INFO,
            {"symbol": "ETHUSDT"},
            signed=False,
        )

    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == (f"{SpotMarket.EXCHANGE_INFO}?symbol=ETHUSDT")


def test_sync_binance_public_wrapper_uses_native_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(preload_product_table=False)
        client._native_client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = client.get_spot_orderbook("BTC-USDT-SPOT", limit=5)

    client.close()
    assert result == {"ok": True}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v3/depth?symbol=BTCUSDT&limit=5"


@pytest.mark.asyncio
async def test_async_binance_public_wrapper_uses_native_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(preload_product_table=False)
        await client.async_init()
        client._native_client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = await client.get_klines("BTC-USDT-SWAP", interval="1m", limit=2)

    await client.close()
    assert result == {"ok": True}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/fapi/v1/klines?symbol=BTCUSDT&interval=1m&limit=2"


def test_sync_binance_private_trade_wrapper_uses_native_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(
            api_key="api-key",
            api_secret="secret",
            preload_product_table=False,
        )
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = client.place_limit_buy_order(
            product_symbol="BTC-USDT-SPOT",
            quantity="1",
            price="100",
        )

    client.close()
    request = _next_non_binance_time_request(received)
    body = dict(parse_qsl(request["body"]))
    assert result == {"ok": True}
    assert request["path"] == "/api/v3/order"
    assert request["api_key"] == "api-key"
    assert body["symbol"] == "BTCUSDT"
    assert body["side"] == "BUY"
    assert body["type"] == "LIMIT"
    assert body["timeInForce"] == "GTC"
    assert "signature" in body


def test_binance_native_dispatcher_uses_product_table_symbols() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(
            api_key="api-key",
            api_secret="secret",
            preload_product_table=False,
        )
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        client._native_client.set_product_table(
            native.ProductTable(
                [
                    {
                        "exchange": "binance",
                        "exchange_symbol": "BTCUSDT_250627",
                        "product_symbol": "BTC-USDT-250627",
                        "product_type": "futures",
                        "exchange_type": "delivery",
                        "price_precision": "0.1",
                        "size_precision": "0.001",
                        "min_size": "0.001",
                        "base_currency": "BTC",
                        "quote_currency": "USDT",
                        "min_notional": "0",
                        "size_per_contract": "1",
                    }
                ]
            )
        )
        result = client.place_limit_buy_order(
            product_symbol="BTC-USDT-250627",
            quantity="1",
            price="100",
        )

    client.close()
    request = _next_non_binance_time_request(received)
    body = dict(parse_qsl(request["body"]))
    assert result == {"ok": True}
    assert request["path"] == "/fapi/v1/order"
    assert body["symbol"] == "BTCUSDT_250627"
    assert body["side"] == "BUY"


@pytest.mark.asyncio
async def test_async_binance_private_account_wrapper_uses_native_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(
            api_key="api-key",
            api_secret="secret",
            preload_product_table=False,
        )
        await client.async_init()
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = await client.get_account_balance(market_type="swap")

    await client.close()
    request = _next_non_binance_time_request(received)
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    assert result == {"ok": True}
    assert urlsplit(request["path"]).path == "/fapi/v3/balance"
    assert request["api_key"] == "api-key"
    assert "signature" in query
