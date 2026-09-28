"""Offline coverage for native http okx."""
# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_okx_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        client = native.OkxHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            flag="1",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "GET",
            "/api/v5/account/balance",
            [("ccy", "BTC")],
            None,
            True,
        )

    request = received.get_nowait()
    timestamp = request["OK-ACCESS-TIMESTAMP"]
    canonical = f"{timestamp}GET/api/v5/account/balance?ccy=BTC"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", canonical.encode(), hashlib.sha256).digest()
    ).decode()

    assert status == 200
    assert body == {"code": "0", "data": []}
    assert request["OK-ACCESS-KEY"] == "api-key"
    assert request["OK-ACCESS-PASSPHRASE"] == "passphrase"
    assert request["OK-ACCESS-SIGN"] == expected_signature
    assert request["x-simulated-trading"] == "1"


def test_sync_okx_manager_uses_native_transport() -> None:
    from dcex.okx._http_manager import HTTPManager

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        manager = HTTPManager(
            base_api=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v5/public/time",
            {"source": "native"},
            signed=False,
        )

    manager.close()
    assert result == {"code": "0", "data": []}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v5/public/time?source=native"


def test_native_okx_spot_borrow_repay_uses_official_paths_and_types() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        client = native.OkxHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            timeout=2,
            base_url=base_url,
        )
        client.private_request_json(
            "spot_manual_borrow_repay",
            [("ccy", "USDT"), ("side", "borrow"), ("amt", "1")],
        )
        client.private_request_json("set_spot_auto_repay", [("autoRepay", "true")])
        client.private_request_json(
            "get_spot_borrow_repay_history",
            [("ccy", "USDT"), ("type", "manual_borrow"), ("limit", "1")],
        )

    borrow = received.get_nowait()
    auto_repay = received.get_nowait()
    history = received.get_nowait()

    assert borrow["path"] == "/api/v5/account/spot-manual-borrow-repay"
    assert json.loads(borrow["body"]) == {
        "ccy": "USDT",
        "side": "borrow",
        "amt": "1",
    }
    assert auto_repay["path"] == "/api/v5/account/set-auto-repay"
    assert json.loads(auto_repay["body"]) == {"autoRepay": True}
    assert history["path"].startswith("/api/v5/account/spot-borrow-repay-history?")
    assert dict(parse_qsl(urlsplit(history["path"]).query)) == {
        "ccy": "USDT",
        "type": "manual_borrow",
        "limit": "1",
    }


@pytest.mark.asyncio
async def test_async_okx_manager_uses_native_transport() -> None:
    from dcex.async_support.okx._http_manager import HTTPManager

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        manager = HTTPManager(
            base_api=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v5/public/time",
            {"source": "native"},
            signed=False,
        )

    assert result == {"code": "0", "data": []}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v5/public/time?source=native"
