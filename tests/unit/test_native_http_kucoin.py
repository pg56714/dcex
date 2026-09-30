"""Offline coverage for native http kucoin."""
# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_kucoin_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": "200000", "data": {}}) as (base_url, received):
        client = native.KucoinHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            timeout=10,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "GET",
            "spot",
            "/api/v1/accounts",
            [("currency", "BTC USDT"), ("type", "trade")],
            None,
            True,
        )

    request = received.get_nowait()
    timestamp = request["KC-API-TIMESTAMP"]
    canonical = f"{timestamp}GET/api/v1/accounts?currency=BTC USDT&type=trade"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", canonical.encode(), hashlib.sha256).digest()
    ).decode()
    expected_passphrase = base64.b64encode(
        hmac.new(b"secret", b"passphrase", hashlib.sha256).digest()
    ).decode()

    assert status == 200
    assert body == {"code": "200000", "data": {}}
    assert request["KC-API-KEY"] == "api-key"
    assert request["KC-API-SIGN"] == expected_signature
    assert request["KC-API-PASSPHRASE"] == expected_passphrase
    assert request["KC-API-KEY-VERSION"] == "2"
    assert request["path"] == "/api/v1/accounts?currency=BTC+USDT&type=trade"


def test_sync_kucoin_manager_uses_native_transport() -> None:
    from dcex.kucoin._http_manager import HTTPManager

    with _http_server({"code": "200000", "data": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v1/timestamp",
            {"source": "native"},
            signed=False,
        )

    manager.close()
    assert result == {"code": "200000", "data": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/timestamp?source=native"


@pytest.mark.asyncio
async def test_async_kucoin_manager_uses_native_transport() -> None:
    from dcex.async_support.kucoin._http_manager import HTTPManager

    with _http_server({"code": "200000", "data": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v1/timestamp",
            {"source": "native"},
            signed=False,
        )

    assert result == {"code": "200000", "data": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/timestamp?source=native"
