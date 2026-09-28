"""Offline coverage for native http hyperliquid."""
# ruff: noqa: D100, D103, F401

import base64
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_hyperliquid_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    action = {"type": "order", "a": 1}

    with _http_server({}) as (base_url, received):
        client = native.HyperliquidHttpClient(
            wallet_address="0x" + "22" * 20,
            private_key="0x" + "11" * 32,
            timeout=2,
            endpoint=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "/exchange",
            json.dumps({"action": action}, separators=(",", ":")).encode(),
            None,
            True,
        )

    request = received.get_nowait()
    payload = json.loads(request["body"])
    assert status == 200
    assert body == {"ok": True}
    assert payload["signature"]["v"] in {27, 28}
    assert payload["signature"]["r"].startswith("0x")
    assert payload["signature"]["s"].startswith("0x")
    assert len(payload["signature"]["r"]) == 66
    assert len(payload["signature"]["s"]) == 66


def test_native_hyperliquid_private_order_builder_fee_payload_matches_docs() -> None:
    native = pytest.importorskip("dcex._native")
    builder_address = "0x0000000000000000000000000000000000000002"

    with _http_server({"ok": True}) as (base_url, received):
        client = native.HyperliquidHttpClient(
            wallet_address="0x" + "22" * 20,
            private_key="0x" + "11" * 32,
            timeout=2,
            endpoint=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_order",
            [
                ("product_symbol", "BTC-USD-SWAP"),
                ("isBuy", "true"),
                ("price", "100"),
                ("size", "1"),
                ("reduceOnly", "false"),
                ("tif", "Gtc"),
                ("builder_address", builder_address),
                ("fee_ten_bp", "10"),
                ("expiresAfter", "1700000001000"),
            ],
        )

    request = received.get_nowait()
    payload = json.loads(request["body"])
    action = payload["action"]
    assert status == 200
    assert body == {"ok": True}
    assert action["builder"] == {"b": builder_address, "f": 10}
    assert action["orders"][0]["t"] == {"limit": {"tif": "Gtc"}}
    assert "feeTenBp" not in action
    assert payload["expiresAfter"] == 1700000001000


def test_native_hyperliquid_market_order_uses_ioc_limit_payload() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server([{"universe": [{"name": "BTC", "szDecimals": 5}]}, [{"midPx": "100.0"}]]) as (
        base_url,
        received,
    ):
        client = native.HyperliquidHttpClient(
            wallet_address="0x" + "22" * 20,
            private_key="0x" + "11" * 32,
            timeout=2,
            endpoint=base_url,
        )
        client.private_request_json(
            "place_future_market_buy_order",
            [("product_symbol", "BTC-USD-SWAP"), ("size", "1")],
        )

    assert received.get_nowait()["path"] == "/info"
    exchange_request = received.get_nowait()
    action = json.loads(exchange_request["body"])["action"]
    order = action["orders"][0]
    assert exchange_request["path"] == "/exchange"
    assert order["p"] == "105"
    assert order["t"] == {"limit": {"tif": "Ioc"}}


def test_sync_hyperliquid_manager_uses_native_transport() -> None:
    from dcex.hyperliquid._http_manager import HTTPManager

    with _http_server({"status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            preload_product_table=False,
        )
        manager.endpoint = base_url
        manager._native_client = pytest.importorskip("dcex._native").HyperliquidHttpClient(
            timeout=2, endpoint=base_url
        )
        result = manager._request(
            "POST",
            "/info",
            {"type": "meta"},
            signed=False,
        )

    manager.close()
    assert result == {"status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/info"


@pytest.mark.asyncio
async def test_async_hyperliquid_manager_uses_native_transport() -> None:
    from dcex.async_support.hyperliquid._http_manager import HTTPManager

    with _http_server({"status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            preload_product_table=False,
        )
        await manager.async_init()
        manager.endpoint = base_url
        manager._native_client = pytest.importorskip("dcex._native").HyperliquidHttpClient(
            timeout=2, endpoint=base_url
        )
        result = await manager._request(
            "POST",
            "/info",
            {"type": "meta"},
            signed=False,
        )

    assert result == {"status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/info"
