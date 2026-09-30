"""Offline coverage for native http bitget."""
# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_bitget_signed_body() -> None:
    native = pytest.importorskip("dcex._native")
    request_body = b'[{"category":"SPOT","symbol":"BTCUSDT","qty":"0.001"}]'

    with _http_server({"code": "00000"}) as (base_url, received):
        client = native.BitgetHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            timeout=10,
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
    payload = f"{request['ACCESS-TIMESTAMP']}POST/test{request_body.decode()}"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", payload.encode(), hashlib.sha256).digest()
    ).decode()

    assert status == 200
    assert body == {"code": "00000"}
    assert request["ACCESS-KEY"] == "api-key"
    assert request["ACCESS-PASSPHRASE"] == "passphrase"
    assert request["ACCESS-SIGN"] == expected_signature
    assert request["body"] == request_body.decode()


def test_sync_bitget_manager_uses_native_transport() -> None:
    from dcex.bitget._http_manager import HTTPManager

    with _http_server({"code": "00000"}) as (base_url, received):
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
    assert result == {"code": "00000"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=BTCUSDT"


def test_native_bitget_crypto_loan_uses_official_paths_and_json_types() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": "00000"}) as (base_url, received):
        client = native.BitgetHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            timeout=10,
            base_url=base_url,
        )
        client.private_request_json(
            "borrow_crypto_loan",
            [
                ("loanCoin", "USDT"),
                ("pledgeCoin", "BTC"),
                ("daily", "FLEXIBLE"),
                ("loanAmount", "1"),
            ],
        )
        client.private_request_json(
            "repay_crypto_loan",
            [("orderId", "loan-1"), ("repayAll", "yes")],
        )
        client.private_request_json("get_crypto_loan_debts", [])
        client.private_request_json(
            "repay_uta_liability",
            [
                ("repayableCoinList", '["USDT"]'),
                ("paymentCoinList", '["BTC","ETH"]'),
            ],
        )

    borrow = received.get_nowait()
    repay = received.get_nowait()
    debts = received.get_nowait()
    uta_repay = received.get_nowait()

    assert borrow["path"] == "/api/v3/loan/borrow"
    assert json.loads(borrow["body"]) == {
        "loanCoin": "USDT",
        "pledgeCoin": "BTC",
        "daily": "FLEXIBLE",
        "loanAmount": "1",
    }
    assert repay["path"] == "/api/v3/loan/repay"
    assert json.loads(repay["body"]) == {"orderId": "loan-1", "repayAll": "yes"}
    assert debts["path"] == "/api/v3/loan/debts"
    assert json.loads(uta_repay["body"]) == {
        "repayableCoinList": ["USDT"],
        "paymentCoinList": ["BTC", "ETH"],
    }


@pytest.mark.asyncio
async def test_async_bitget_manager_uses_native_transport() -> None:
    from dcex.async_support.bitget._http_manager import HTTPManager

    with _http_server({"code": "00000"}) as (base_url, received):
        manager = HTTPManager(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "POST",
            "/test",
            [{"symbol": "BTCUSDT", "qty": "1"}],
            signed=True,
        )

    request = received.get_nowait()
    assert result == {"code": "00000"}
    assert manager.last_response_headers["x-response"] == "native"
    assert request["body"] == '[{"symbol":"BTCUSDT","qty":"1"}]'
