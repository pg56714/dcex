"""Regression coverage for the current Backpack REST and WebSocket surface."""

# ruff: noqa: D103

from __future__ import annotations

import base64
import inspect
import json
from enum import Enum
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)
from tests.unit.native_http_helpers import _http_server

CURRENT_FIELDS = {
    "get_markets": {"marketType"},
    "get_klines": {"product_symbol", "interval", "startTime", "source"},
    "get_ticker": {"product_symbol", "interval", "source"},
    "get_tickers": {"interval", "source"},
    "get_borrow_history": {"type_", "sources", "positionId", "symbol"},
    "get_interest_history": {"asset", "symbol", "positionId", "source"},
    "get_fill_history": {"strategyId", "from_", "to", "fillType", "assetClass"},
    "get_order_history": {"strategyId", "marketType"},
    "get_open_positions": {"product_symbol", "marketType"},
    "place_order": {"brokerId", "brokerKey"},
    "place_market_order": {
        "selfTradePrevention",
        "stopLossTriggerPrice",
        "slippageToleranceType",
        "brokerId",
        "brokerKey",
    },
    "place_limit_order": {
        "selfTradePrevention",
        "takeProfitTriggerPrice",
        "slippageToleranceType",
        "brokerId",
        "brokerKey",
    },
    "place_batch_orders": {"orders", "brokerId"},
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_backpack_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "backpack")
    async_client = _client_class("async", "backpack")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


def test_backpack_liquidation_stream_requires_a_symbol() -> None:
    from dcex.ws.backpack import PublicClient

    parameter = inspect.signature(PublicClient.subscribe_liquidation).parameters[
        "product_symbol"
    ]

    assert parameter.default is inspect.Parameter.empty


def test_backpack_native_params_expand_repeated_enum_values() -> None:
    from dcex.backpack._http_manager import HTTPManager

    class MarketType(Enum):
        SPOT = "SPOT"
        PERP = "PERP"

    assert HTTPManager._native_params(
        marketType=[MarketType.SPOT, MarketType.PERP],
        type_="Borrow",
        enabled=True,
    ) == [
        ("marketType", "SPOT"),
        ("marketType", "PERP"),
        ("type", "Borrow"),
        ("enabled", "true"),
    ]


def test_sync_backpack_forwards_current_fields() -> None:
    client = _client_class("sync", "backpack")(**_client_kwargs("backpack"))
    calls = _wire_sync(client)

    client.get_markets(marketType=["SPOT", "RFQ"])
    client.get_borrow_history(
        type_="BorrowRepay",
        sources="SpotMargin,AutoBorrow",
        positionId="position-1",
    )
    client.get_fill_history(
        strategyId="strategy-1",
        from_=1_000,
        to=2_000,
        fillType="User",
        marketType=["SPOT", "PERP"],
        assetClass="CRYPTO",
    )

    assert calls[0]["query"] == [("marketType", "SPOT"), ("marketType", "RFQ")]
    assert dict(calls[1]["query"]) == {
        "type": "BorrowRepay",
        "sources": "SpotMargin,AutoBorrow",
        "positionId": "position-1",
    }
    assert calls[2]["query"] == [
        ("strategyId", "strategy-1"),
        ("from", "1000"),
        ("to", "2000"),
        ("fillType", "User"),
        ("marketType", "SPOT"),
        ("marketType", "PERP"),
        ("assetClass", "CRYPTO"),
    ]


@pytest.mark.asyncio
async def test_async_backpack_forwards_current_fields() -> None:
    client = _client_class("async", "backpack")(**_client_kwargs("backpack"))
    calls = _wire_async(client)

    await client.get_klines(
        "MU.US_USDC",
        "1m",
        1_000,
        endTime=2_000,
        priceType="Last",
        source="External",
    )
    await client.get_interest_history(
        asset="USDC",
        positionId="position-1",
        source="BorrowLend",
    )
    await client.get_open_positions(marketType="PERP")

    assert dict(calls[0]["query"]) == {
        "product_symbol": "MU.US_USDC",
        "interval": "1m",
        "startTime": "1000",
        "endTime": "2000",
        "priceType": "Last",
        "source": "External",
    }
    assert dict(calls[1]["query"]) == {
        "asset": "USDC",
        "positionId": "position-1",
        "source": "BorrowLend",
    }
    assert calls[2]["query"] == [("marketType", "PERP")]


def _native_client(*, base_url: str = "http://127.0.0.1:1", private: bool = False) -> object:
    native = pytest.importorskip("dcex._native")
    kwargs: dict[str, object] = {"timeout": 2, "base_url": base_url}
    if private:
        kwargs.update(
            api_key=base64.b64encode(b"2" * 32).decode(),
            api_secret=base64.b64encode(b"1" * 32).decode(),
        )
    return native.BackpackHttpClient(**kwargs)


def test_backpack_current_public_queries_match_wire_format() -> None:
    with _http_server({"ok": True}) as (base_url, received):
        client = _native_client(base_url=base_url)
        client.public_request_json(
            "get_markets",
            [("marketType", "SPOT"), ("marketType", "RFQ")],
        )
        client.public_request_json(
            "get_klines",
            [
                ("symbol", "MU.US_USDC"),
                ("interval", "1m"),
                ("startTime", "1000"),
                ("endTime", "2000"),
                ("priceType", "Last"),
                ("source", "External"),
            ],
        )

    markets = urlsplit(received.get_nowait()["path"])
    klines = urlsplit(received.get_nowait()["path"])
    assert markets.path == "/api/v1/markets"
    assert parse_qsl(markets.query) == [("marketType", "SPOT"), ("marketType", "RFQ")]
    assert klines.path == "/api/v1/klines"
    assert dict(parse_qsl(klines.query)) == {
        "interval": "1m",
        "startTime": "1000",
        "endTime": "2000",
        "priceType": "Last",
        "source": "External",
        "symbol": "MU.US_USDC",
    }


def test_backpack_current_private_queries_and_order_headers_match_wire_format() -> None:
    with _http_server({"ok": True}) as (base_url, received):
        client = _native_client(base_url=base_url, private=True)
        client.private_request_json(
            "get_borrow_history",
            [
                ("type", "BorrowRepay"),
                ("sources", "SpotMargin,AutoBorrow"),
                ("positionId", "position-1"),
                ("limit", "1000"),
            ],
        )
        client.private_request_json(
            "get_fill_history",
            [
                ("strategyId", "strategy-1"),
                ("marketType", "SPOT"),
                ("marketType", "PERP"),
                ("assetClass", "CRYPTO"),
            ],
        )
        client.private_request_json(
            "place_limit_order",
            [
                ("symbol", "BTC_USDC"),
                ("side", "Bid"),
                ("quantity", "1"),
                ("price", "100"),
                ("selfTradePrevention", "RejectBoth"),
                ("brokerId", "42"),
                ("brokerKey", "broker-secret"),
            ],
        )

    borrow = urlsplit(received.get_nowait()["path"])
    fills = urlsplit(received.get_nowait()["path"])
    order = received.get_nowait()
    assert borrow.path == "/wapi/v1/history/borrowLend"
    assert dict(parse_qsl(borrow.query))["type"] == "BorrowRepay"
    assert fills.path == "/wapi/v1/history/fills"
    assert parse_qsl(fills.query).count(("marketType", "SPOT")) == 1
    assert parse_qsl(fills.query).count(("marketType", "PERP")) == 1
    assert order["path"] == "/api/v1/order"
    assert order["backpack_x-broker-id"] == "42"
    assert order["backpack_x-broker-key"] == "broker-secret"
    assert json.loads(order["body"]) == {
        "side": "Bid",
        "quantity": "1",
        "price": "100",
        "timeInForce": "GTC",
        "selfTradePrevention": "RejectBoth",
        "symbol": "BTC_USDC",
        "orderType": "Limit",
    }


def test_backpack_rejects_invalid_current_parameters_before_transport() -> None:
    client = _native_client()
    with pytest.raises(ValueError, match="unsupported Backpack parameter"):
        client.public_request_json("get_status", [("unexpected", "1")])
    with pytest.raises(ValueError, match="priceType=Last"):
        client.public_request_json(
            "get_klines",
            [
                ("symbol", "MU.US_USDC"),
                ("interval", "1m"),
                ("startTime", "1000"),
                ("priceType", "Mark"),
                ("source", "External"),
            ],
        )

    private = _native_client(private=True)
    with pytest.raises(ValueError, match="exactly one"):
        private.private_request_json(
            "cancel_order",
            [
                ("symbol", "BTC_USDC"),
                ("orderId", "order-1"),
                ("clientId", "1"),
            ],
        )
    with pytest.raises(ValueError, match="between 1 and 50"):
        private.private_request_json("place_batch_orders", [("orders", "[]")])


def test_backpack_rejects_window_above_official_maximum() -> None:
    native = pytest.importorskip("dcex._native")
    with pytest.raises(ValueError, match="60000"):
        native.BackpackHttpClient(window=60_001, timeout=2)
