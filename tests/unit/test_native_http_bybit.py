"""Offline coverage for native http bybit."""
# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_bybit_signed_body() -> None:
    native = pytest.importorskip("dcex._native")
    request_body = b'{"symbol":"BTCUSDT","qty":"1"}'

    with _http_server({"retCode": 0}) as (base_url, received):
        client = native.BybitHttpClient(
            api_key="api-key",
            api_secret="secret",
            recv_window=5000,
            sync_server_time=False,
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "/test",
            [],
            request_body,
            True,
        )

    request = received.get_nowait()
    payload = (
        f"{request['X-BAPI-TIMESTAMP']}api-key"
        f"{request['X-BAPI-RECV-WINDOW']}{request_body.decode()}"
    )
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert body == {"retCode": 0}
    assert request["X-BAPI-API-KEY"] == "api-key"
    assert request["X-BAPI-SIGN"] == expected_signature
    assert request["body"] == request_body.decode()


def test_sync_bybit_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.bybit._http_manager import HTTPManager

    with _http_server({"retCode": 0}) as (base_url, received):
        manager = HTTPManager(
            preload_product_table=False,
            sync_server_time=False,
        )
        manager._native_client = native.BybitHttpClient(
            sync_server_time=False,
            timeout=2,
            base_url=base_url,
        )
        result = manager._request(
            "GET",
            "/test",
            {"symbol": "BTCUSDT"},
            signed=False,
        )

    manager.close()
    assert result == {"retCode": 0}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=BTCUSDT"


@pytest.mark.asyncio
async def test_async_bybit_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.bybit._http_manager import HTTPManager

    with _http_server({"retCode": 0}) as (base_url, received):
        manager = HTTPManager(
            preload_product_table=False,
            sync_server_time=False,
        )
        await manager.async_init()
        manager._native_client = native.BybitHttpClient(
            sync_server_time=False,
            timeout=2,
            base_url=base_url,
        )
        result = await manager._request(
            "GET",
            "/test",
            {"symbol": "ETHUSDT"},
            signed=False,
        )

    assert result == {"retCode": 0}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=ETHUSDT"


def test_native_bybit_margin_lifecycle_uses_official_paths_and_payloads() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"retCode": 0}) as (base_url, received):
        client = native.BybitHttpClient(
            api_key="api-key",
            api_secret="secret",
            sync_server_time=False,
            timeout=2,
            base_url=base_url,
        )
        client.private_request_json("manual_borrow", [("coin", "USDT"), ("amount", "1")])
        client.private_request_json(
            "manual_repay_without_conversion",
            [
                ("coin", "USDT"),
                ("amount", "1"),
                ("repaymentType", "FLEXIBLE"),
            ],
        )
        client.private_request_json("get_margin_liability", [("currency", "USDT")])
        client.private_request_json(
            "borrow_fixed_rate",
            [
                ("orderCurrency", "USDT"),
                ("orderAmount", "10"),
                ("annualRate", "0.02"),
                ("term", "7"),
            ],
        )

    borrow = received.get_nowait()
    repay = received.get_nowait()
    liability = received.get_nowait()
    fixed = received.get_nowait()

    assert borrow["path"] == "/v5/account/borrow"
    assert json.loads(borrow["body"]) == {"coin": "USDT", "amount": "1"}
    assert repay["path"] == "/v5/account/no-convert-repay"
    assert json.loads(repay["body"]) == {
        "coin": "USDT",
        "amount": "1",
        "repaymentType": "FLEXIBLE",
    }
    assert liability["path"].startswith("/v5/spot-margin-trade/liability?")
    assert dict(parse_qsl(urlsplit(liability["path"]).query))["currency"] == "USDT"
    assert fixed["path"] == "/v5/spot-margin-trade/fixedborrow"
    assert json.loads(fixed["body"]) == {
        "orderCurrency": "USDT",
        "orderAmount": "10",
        "annualRate": "0.02",
        "term": "7",
    }
