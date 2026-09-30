"""Offline coverage for native http extended."""
# ruff: noqa: D100, D103, F401

import base64
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_extended_signed_request_uses_api_key_and_user_agent() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"status": "OK"}) as (base_url, received):
        client = native.ExtendedHttpClient(
            api_key="extended-key",
            timeout=10,
            base_url=base_url,
            user_agent="dcex-test",
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "/api/v1/user/order",
            None,
            b'{"market":"BTC-USD"}',
            True,
            None,
        )

    request = received.get_nowait()
    assert status == 200
    assert body == {"status": "OK"}
    assert request["path"] == "/api/v1/user/order"
    assert request["body"] == '{"market":"BTC-USD"}'
    assert request["extended_x-api-key"] == "extended-key"
    assert request["extended_user-agent"] == "dcex-test"


def test_sync_extended_wrapper_uses_native_dispatcher() -> None:
    pytest.importorskip("dcex._native")
    from dcex.extended.client import Client

    with _http_server({"status": "OK", "data": []}) as (base_url, received):
        client = Client(
            base_url=base_url,
            preload_product_table=False,
            user_agent="dcex-test",
        )
        result = client.get_markets()

    client.close()
    assert result == {"status": "OK", "data": []}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/info/markets"


def test_sync_extended_market_methods_use_documented_paths() -> None:
    pytest.importorskip("dcex._native")
    from dcex.extended.client import Client

    with _http_server({"status": "OK"}) as (base_url, received):
        client = Client(
            base_url=base_url,
            preload_product_table=False,
            user_agent="dcex-test",
        )
        client.get_assets(asset="BTC", type="SPOT", collateral=False)
        client.get_market_statistics("BTC-USD")
        client.get_order_book("BTC-USD")
        client.get_trades("BTC-USD")
        client.get_candles("BTC-USD", "PT1M", candleType="mark-prices", limit=50, endTime=123)
        client.get_funding("BTC-USD", startTime=100, endTime=200, limit=10)
        client.get_open_interest("BTC-USD", "P1H", startTime=100, endTime=200, limit=10)

    client.close()
    assert (
        received.get_nowait()["path"] == "/api/v1/info/assets?asset=BTC&type=SPOT&collateral=false"
    )
    assert received.get_nowait()["path"] == "/api/v1/info/markets/BTC-USD/stats"
    assert received.get_nowait()["path"] == "/api/v1/info/markets/BTC-USD/orderbook"
    assert received.get_nowait()["path"] == "/api/v1/info/markets/BTC-USD/trades"
    assert (
        received.get_nowait()["path"]
        == "/api/v1/info/candles/BTC-USD/mark-prices?interval=PT1M&limit=50&endTime=123"
    )
    assert (
        received.get_nowait()["path"]
        == "/api/v1/info/BTC-USD/funding?startTime=100&endTime=200&limit=10"
    )
    assert (
        received.get_nowait()["path"]
        == "/api/v1/info/BTC-USD/open-interests?interval=P1H&startTime=100&endTime=200&limit=10"
    )


def test_sync_extended_candles_require_limit() -> None:
    pytest.importorskip("dcex._native")
    from dcex.extended.client import Client

    client = Client(
        base_url="http://127.0.0.1:1",
        preload_product_table=False,
        user_agent="dcex-test",
    )
    with pytest.raises(ValueError, match="limit is required for Extended candles"):
        client.get_candles("BTC-USD", "PT1M")
    client.close()


def test_sync_extended_get_order_uses_plural_order_path() -> None:
    pytest.importorskip("dcex._native")
    from dcex.extended.client import Client

    with _http_server({"status": "OK"}) as (base_url, received):
        client = Client(
            api_key="extended-key",
            base_url=base_url,
            preload_product_table=False,
            user_agent="dcex-test",
        )
        client.get_order("123")
        client.get_order_by_external_id("client-123")
        client.get_spot_balances(accountId=100)
        client.get_fees(market="BTC-USD", builderId=2017)
        client.set_deadmanswitch(countdownTime=60)

    client.close()
    request = received.get_nowait()
    assert request["path"] == "/api/v1/user/orders/123"
    assert request["extended_x-api-key"] == "extended-key"
    assert received.get_nowait()["path"] == "/api/v1/user/orders/external/client-123"
    assert received.get_nowait()["path"] == "/api/v1/user/spot/balances?accountId=100"
    assert received.get_nowait()["path"] == "/api/v1/user/fees?market=BTC-USD&builderId=2017"
    deadman_request = received.get_nowait()
    assert deadman_request["path"] == "/api/v1/user/deadmanswitch?countdownTime=60"
    assert deadman_request["body"] == ""


@pytest.mark.asyncio
async def test_async_extended_wrapper_uses_native_dispatcher() -> None:
    pytest.importorskip("dcex._native")
    from dcex.async_support.extended.client import Client

    with _http_server({"status": "OK", "data": []}) as (base_url, received):
        client = Client(
            base_url=base_url,
            preload_product_table=False,
            user_agent="dcex-test",
        )
        await client.async_init()
        result = await client.get_assets()

    await client.close()
    assert result == {"status": "OK", "data": []}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/info/assets"
