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
        status, _headers, body = client.request_raw(
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
    assert json.loads(body) == {"ok": True}
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


def test_native_lighter_form_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": 0}) as (base_url, received):
        client = native.LighterHttpClient(timeout=2, base_url=base_url)
        status, _headers, body = client.request_raw(
            "POST",
            "/api/v1/sendTx",
            [("account_index", "1")],
            [("tx_type", "14"), ("tx_info", '{"Price":100}')],
            False,
            {"Authorization": "token"},
            "form",
        )

    request = received.get_nowait()
    assert status == 200
    assert json.loads(body) == {"code": 0}
    assert request["path"] == "/api/v1/sendTx?account_index=1"
    assert request["body"] == "tx_type=14&tx_info=%7B%22Price%22%3A100%7D"


def test_sync_lighter_manager_uses_native_transport() -> None:
    from dcex.lighter._http_manager import HTTPManager

    with _http_server({"code": 0, "status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v1/status",
            {"source": "native"},
        )

    manager.close()
    assert result == {"code": 0, "status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/status?source=native"


@pytest.mark.asyncio
async def test_async_lighter_manager_uses_native_transport() -> None:
    from dcex.async_support.lighter._http_manager import HTTPManager

    with _http_server({"code": 0, "status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v1/status",
            {"source": "native"},
        )

    assert result == {"code": 0, "status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/status?source=native"


def test_native_aster_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    signer = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"

    with _http_server({}) as (base_url, received):
        client = native.AsterHttpClient(
            signer_address=signer,
            private_key="0x" + "11" * 32,
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "spot",
            "/api/v3/order",
            [("symbol", "BTCUSDT"), ("side", "BUY")],
            True,
        )

    request = received.get_nowait()
    pairs = parse_qsl(request["body"])
    signature = dict(pairs)["signature"]
    message = "&".join(f"{key}={value}" for key, value in pairs[:-1])
    from dcex.aster._http_manager import sign_message

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert signature == sign_message(message, "0x" + "11" * 32)


def test_sync_aster_public_wrapper_uses_native_dispatcher() -> None:
    pytest.importorskip("dcex._native")
    from dcex.aster.client import Client

    with _http_server({"serverTime": 1}) as (base_url, received):
        client = Client(
            spot_base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = client.get_spot_server_time()

    client.close()
    assert result == {"serverTime": 1}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v3/time"


@pytest.mark.asyncio
async def test_async_aster_public_wrapper_uses_native_dispatcher() -> None:
    pytest.importorskip("dcex._native")
    from dcex.async_support.aster.client import Client

    with _http_server({"serverTime": 1}) as (base_url, received):
        client = Client(
            spot_base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await client.async_init()
        result = await client.get_futures_server_time()

    await client.close()
    assert result == {"serverTime": 1}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/fapi/v3/time"


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
        status, _headers, body = client.request_raw(
            "POST",
            "/exchange",
            json.dumps({"action": action}, separators=(",", ":")).encode(),
            None,
            True,
        )

    request = received.get_nowait()
    payload = json.loads(request["body"])
    assert status == 200
    assert json.loads(body) == {"ok": True}
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
        status, _headers, body = client.private_request(
            "place_order",
            [
                ("product_symbol", "BTC-USD-SWAP"),
                ("isBuy", "true"),
                ("price", "100"),
                ("size", "1"),
                ("reduceOnly", "false"),
                ("builder_address", builder_address),
                ("fee_ten_bp", "10"),
            ],
        )

    request = received.get_nowait()
    action = json.loads(request["body"])["action"]
    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert action["builder"] == {"b": builder_address, "f": 10}
    assert "feeTenBp" not in action


def test_native_hyperliquid_market_order_uses_ioc_limit_payload() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server([{}, [{"midPx": "100.0"}]]) as (base_url, received):
        client = native.HyperliquidHttpClient(
            wallet_address="0x" + "22" * 20,
            private_key="0x" + "11" * 32,
            timeout=2,
            endpoint=base_url,
        )
        client.private_request(
            "place_future_market_buy_order",
            [("product_symbol", "BTC-USD-SWAP"), ("size", "1")],
        )

    assert received.get_nowait()["path"] == "/info"
    exchange_request = received.get_nowait()
    action = json.loads(exchange_request["body"])["action"]
    order = action["orders"][0]
    assert exchange_request["path"] == "/exchange"
    assert order["p"] == "103"
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
