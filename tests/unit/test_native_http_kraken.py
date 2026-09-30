"""Offline coverage for native http kraken."""
# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_kraken_spot_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    api_secret = base64.b64encode(b"secret").decode()

    with _http_server({"error": [], "result": {}}) as (base_url, received):
        client = native.KrakenHttpClient(
            spot_api_key="api-key",
            spot_api_secret=api_secret,
            timeout=10,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "spot",
            "/0/private/Balance",
            [("asset", "BTC USD")],
            None,
            True,
        )

    request = received.get_nowait()
    encoded_body = request["body"]
    nonce = dict(parse_qsl(encoded_body))["nonce"]
    digest = hashlib.sha256((nonce + encoded_body).encode()).digest()
    expected_signature = base64.b64encode(
        hmac.new(b"secret", b"/0/private/Balance" + digest, hashlib.sha512).digest()
    ).decode()

    assert status == 200
    assert body == {"error": [], "result": {}}
    assert request["kraken_api-key"] == "api-key"
    assert request["kraken_api-sign"] == expected_signature
    assert request["path"] == "/0/private/Balance"


def test_native_kraken_futures_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    api_secret = base64.b64encode(b"secret").decode()

    with _http_server({"result": "success"}) as (base_url, received):
        client = native.KrakenHttpClient(
            futures_api_key="api-key",
            futures_api_secret=api_secret,
            timeout=10,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "futures",
            "/derivatives/api/v3/sendorder",
            [("symbol", "PI_XBTUSD"), ("side", "buy")],
            None,
            True,
        )

    request = received.get_nowait()
    post_data = request["body"]
    nonce = request["kraken_nonce"]
    digest = hashlib.sha256((post_data + nonce + "/api/v3/sendorder").encode()).digest()
    expected_signature = base64.b64encode(
        hmac.new(b"secret", digest, hashlib.sha512).digest()
    ).decode()

    assert status == 200
    assert body == {"result": "success"}
    assert request["kraken_apikey"] == "api-key"
    assert request["kraken_authent"] == expected_signature


def test_sync_kraken_manager_uses_native_transport() -> None:
    from dcex.kraken._http_manager import HTTPManager

    with _http_server({"error": [], "result": {"unixtime": 1}}) as (
        base_url,
        received,
    ):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/0/public/Time",
            signed=False,
        )

    manager.close()
    assert result == {"error": [], "result": {"unixtime": 1}}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/0/public/Time"


@pytest.mark.asyncio
async def test_async_kraken_manager_uses_native_transport() -> None:
    from dcex.async_support.kraken._http_manager import HTTPManager

    with _http_server({"error": [], "result": {"unixtime": 1}}) as (
        base_url,
        received,
    ):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/0/public/Time",
            signed=False,
        )

    assert result == {"error": [], "result": {"unixtime": 1}}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/0/public/Time"
