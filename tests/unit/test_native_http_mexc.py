"""Offline coverage for native http mexc."""
# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_mexc_spot_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=10,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "GET",
            "spot",
            "/test",
            [("symbol", "BTCUSDT")],
            None,
            True,
        )

    time_request = received.get_nowait()
    request = received.get_nowait()
    pairs = parse_qsl(urlsplit(request["path"]).query)
    payload = "&".join(f"{key}={value}" for key, value in pairs[:-1])
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert body == {"ok": True}
    assert time_request["path"] == "/api/v3/time"
    assert request["X-MEXC-APIKEY"] == "api-key"
    assert pairs[-1] == ("signature", expected_signature)


def test_native_mexc_contract_signed_body() -> None:
    native = pytest.importorskip("dcex._native")
    request_body = b'[{"orderId":"1"},{"orderId":"2"}]'

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=10,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "contract",
            "/test",
            [],
            request_body,
            True,
        )

    request = received.get_nowait()
    expected_signature = hmac.new(
        b"secret",
        f"api-key{request['Request-Time']}{request_body.decode()}".encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert body == {"ok": True}
    assert request["ApiKey"] == "api-key"
    assert request["Signature"] == expected_signature
    assert request["body"] == request_body.decode()


def test_sync_mexc_manager_uses_native_transport() -> None:
    from dcex.mexc._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            contract_base_url=base_url,
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


@pytest.mark.asyncio
async def test_async_mexc_manager_uses_native_contract_transport() -> None:
    from dcex.async_support.mexc._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            api_key="api-key",
            api_secret="secret",
            base_url=base_url,
            contract_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "POST",
            "/test",
            [{"orderId": "1"}, {"orderId": "2"}],
            signed=True,
            api="contract",
        )

    request = received.get_nowait()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert request["body"] == '[{"orderId":"1"},{"orderId":"2"}]'


def test_native_mexc_public_dispatcher_normalizes_product_symbol() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=10,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.public_request_json(
            "get_contract_depth",
            [("product_symbol", "BTC_USDT"), ("limit", "5")],
        )

    request = received.get_nowait()
    assert status == 200
    assert body == {"ok": True}
    assert request["path"] == "/api/v1/contract/depth/BTC_USDT?limit=5"


def test_native_mexc_private_spot_batch_order_converts_product_symbols() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=10,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_spot_batch_orders",
            [
                (
                    "batchOrders",
                    json.dumps(
                        [
                            {
                                "product_symbol": "BTC-USDT-SPOT",
                                "side": "BUY",
                                "type": "LIMIT_MAKER",
                                "quantity": "1",
                                "price": "1",
                            }
                        ],
                        separators=(",", ":"),
                    ),
                )
            ],
        )

    time_request = received.get_nowait()
    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    batch_orders = json.loads(query["batchOrders"])
    assert status == 200
    assert body == {"ok": True}
    assert time_request["path"] == "/api/v3/time"
    assert urlsplit(request["path"]).path == "/api/v3/batchOrders"
    assert batch_orders[0]["symbol"] == "BTCUSDT"
    assert "product_symbol" not in batch_orders[0]
    assert "signature" in query


def test_native_mexc_private_contract_order_builds_json_body() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=10,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_contract_order",
            [
                ("product_symbol", "BTC_USDT"),
                ("side", "1"),
                ("type", "2"),
                ("openType", "2"),
                ("vol", "1"),
                ("price", "100"),
                ("leverage", "50"),
                ("reduceOnly", "false"),
            ],
        )

    request = received.get_nowait()
    payload = json.loads(request["body"])
    assert status == 200
    assert body == {"ok": True}
    assert request["path"] == "/api/v1/private/order/create"
    assert payload["symbol"] == "BTC_USDT"
    assert payload["side"] == 1
    assert payload["type"] == 2
    assert payload["openType"] == 2
    assert payload["vol"] == 1
    assert payload["reduceOnly"] is False
