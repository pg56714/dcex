"""Offline coverage for native http backpack."""
# ruff: noqa: D100, D103, F401

import base64
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_backpack_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    api_key = base64.b64encode(b"2" * 32).decode()
    api_secret = base64.b64encode(b"1" * 32).decode()

    with _http_server({}) as (base_url, received):
        client = native.BackpackHttpClient(
            api_key=api_key,
            api_secret=api_secret,
            window=5000,
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "GET",
            "/api/v1/order",
            [("symbol", "BTC_USDC"), ("orderId", "test-order-id")],
            None,
            True,
            "orderQuery",
            [[("symbol", "BTC_USDC"), ("orderId", "test-order-id")]],
            None,
        )

    request = received.get_nowait()
    assert status == 200
    assert body == {"ok": True}
    assert request["backpack_x-api-key"] == api_key
    assert len(base64.b64decode(request["backpack_x-signature"])) == 64
    assert request["path"] == ("/api/v1/order?symbol=BTC_USDC&orderId=test-order-id")


def test_sync_backpack_manager_uses_native_transport() -> None:
    pytest.importorskip("dcex._native")
    from dcex.backpack._http_manager import HTTPManager

    with _http_server({"serverTime": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v1/time",
            signed=False,
        )

    manager.close()
    assert result == {"serverTime": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/time"


@pytest.mark.asyncio
async def test_async_backpack_manager_uses_native_transport() -> None:
    pytest.importorskip("dcex._native")
    from dcex.async_support.backpack._http_manager import HTTPManager

    with _http_server({"serverTime": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v1/time",
            signed=False,
        )

    assert result == {"serverTime": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/time"
