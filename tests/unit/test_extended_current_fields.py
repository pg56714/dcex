"""Regression coverage for the current Extended REST and WebSocket surface."""

# ruff: noqa: D103

from __future__ import annotations

import inspect
from enum import Enum
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


@pytest.mark.parametrize(
    ("method_name", "expected"),
    [
        ("get_markets", {"market"}),
        ("get_assets", {"asset", "type", "collateral"}),
        ("get_asset_operations", {"accountId", "id", "type", "status", "startTime", "endTime"}),
        ("get_spot_balances", {"accountId"}),
        ("get_orders_history", {"id", "externalId", "market", "type", "side", "sort"}),
        ("get_funding_payments", {"startTime", "market", "side", "cursor", "limit"}),
        ("get_fees", {"market", "builderId"}),
    ],
)
def test_extended_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    from dcex.async_support.extended.client import Client as AsyncClient
    from dcex.extended.client import Client as SyncClient

    sync_fields = set(inspect.signature(getattr(SyncClient, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(AsyncClient, method_name)).parameters)
    assert expected <= sync_fields
    assert sync_fields == async_fields


def test_extended_funding_payments_requires_start_time() -> None:
    from dcex.extended.client import Client

    parameter = inspect.signature(Client.get_funding_payments).parameters["startTime"]
    assert parameter.default is inspect.Parameter.empty


def test_extended_native_params_expand_repeated_values() -> None:
    from dcex.extended._http_manager import HTTPManager

    class AssetType(Enum):
        SPOT = "SPOT"
        PERPETUAL = "PERPETUAL"

    assert HTTPManager._native_params(
        market=["BTC-USD", "ETH-USD"],
        type_=[AssetType.SPOT, AssetType.PERPETUAL],
        enabled=True,
    ) == [
        ("market", "BTC-USD"),
        ("market", "ETH-USD"),
        ("type", "SPOT"),
        ("type", "PERPETUAL"),
        ("enabled", "true"),
    ]


def _native_client(*, base_url: str = "http://127.0.0.1:1", private: bool = False) -> object:
    native = pytest.importorskip("dcex._native")
    return native.ExtendedHttpClient(
        api_key="extended-key" if private else None,
        timeout=2,
        base_url=base_url,
        user_agent="dcex-test",
    )


def test_extended_current_public_queries_match_wire_format() -> None:
    with _http_server({"status": "OK", "data": []}) as (base_url, received):
        client = _native_client(base_url=base_url)
        client.public_request_json(
            "get_markets",
            [("market", "BTC-USD"), ("market", "ETH-USD")],
        )
        client.public_request_json(
            "get_candles",
            [
                ("market", "BTC-USD"),
                ("candleType", "trades"),
                ("interval", "PT1M"),
                ("limit", "100"),
            ],
        )
        client.public_request_json(
            "get_open_interest",
            [
                ("market", "BTC-USD"),
                ("interval", "P1H"),
                ("startTime", "100"),
                ("endTime", "200"),
                ("limit", "300"),
            ],
        )
        client.public_request_json(
            "get_market_statistics",
            [("product_symbol", "BTC-USDC-SPOT")],
        )

    markets = urlsplit(received.get_nowait()["path"])
    candles = urlsplit(received.get_nowait()["path"])
    open_interest = urlsplit(received.get_nowait()["path"])
    spot_stats = received.get_nowait()
    assert parse_qsl(markets.query) == [("market", "BTC-USD"), ("market", "ETH-USD")]
    assert candles.path == "/api/v1/info/candles/BTC-USD/trades"
    assert dict(parse_qsl(candles.query)) == {"interval": "PT1M", "limit": "100"}
    assert open_interest.path == "/api/v1/info/BTC-USD/open-interests"
    assert dict(parse_qsl(open_interest.query))["interval"] == "P1H"
    assert spot_stats["path"] == "/api/v1/info/markets/BTCSPOT/stats"


def test_extended_current_private_queries_match_wire_format() -> None:
    with _http_server({"status": "OK", "data": []}) as (base_url, received):
        client = _native_client(base_url=base_url, private=True)
        client.private_request_json(
            "get_asset_operations",
            [
                ("accountId", "100"),
                ("accountId", "101"),
                ("type", "DEPOSIT"),
                ("type", "WITHDRAWAL"),
                ("status", "COMPLETED"),
                ("startTime", "100"),
                ("endTime", "200"),
                ("limit", "50"),
            ],
        )
        client.private_request_json(
            "get_orders_history",
            [
                ("id", "1"),
                ("id", "2"),
                ("externalId", "client-1"),
                ("sort", "UPDATED_AT"),
            ],
        )
        client.private_request_json(
            "get_funding_payments",
            [("startTime", "100"), ("limit", "1000")],
        )

    operations = urlsplit(received.get_nowait()["path"])
    orders = urlsplit(received.get_nowait()["path"])
    funding = urlsplit(received.get_nowait()["path"])
    assert operations.path == "/api/v1/user/assetOperations"
    assert parse_qsl(operations.query).count(("accountId", "100")) == 1
    assert parse_qsl(operations.query).count(("accountId", "101")) == 1
    assert parse_qsl(operations.query).count(("type", "DEPOSIT")) == 1
    assert parse_qsl(operations.query).count(("type", "WITHDRAWAL")) == 1
    assert parse_qsl(orders.query).count(("id", "1")) == 1
    assert parse_qsl(orders.query).count(("id", "2")) == 1
    assert dict(parse_qsl(funding.query)) == {"startTime": "100", "limit": "1000"}


def test_extended_rejects_invalid_current_parameters_before_transport() -> None:
    public = _native_client()
    with pytest.raises(ValueError, match="unsupported Extended candle interval"):
        public.public_request_json(
            "get_candles",
            [("market", "BTC-USD"), ("interval", "1m"), ("limit", "100")],
        )
    with pytest.raises(ValueError, match="between 1 and 300"):
        public.public_request_json(
            "get_open_interest",
            [
                ("market", "BTC-USD"),
                ("interval", "P1H"),
                ("startTime", "100"),
                ("endTime", "200"),
                ("limit", "301"),
            ],
        )
    with pytest.raises(ValueError, match="must not be after"):
        public.public_request_json(
            "get_funding",
            [("market", "BTC-USD"), ("startTime", "200"), ("endTime", "100")],
        )

    private = _native_client(private=True)
    with pytest.raises(ValueError, match="missing required parameter: startTime"):
        private.private_request_json("get_funding_payments", [("limit", "20")])
    with pytest.raises(ValueError, match="expected one of"):
        private.private_request_json("get_open_orders", [("type", "MARKET")])
    with pytest.raises(ValueError, match="at least one field"):
        private.private_request_json("mass_cancel", [("body", "{}")])
    with pytest.raises(ValueError, match="missing required JSON field: id"):
        private.private_request_json(
            "place_order",
            [("body", '{"market":"BTC-USD","type":"LIMIT"}')],
        )


@pytest.mark.asyncio
async def test_extended_rejects_empty_credentials_and_invalid_ws_values() -> None:
    native = pytest.importorskip("dcex._native")
    with pytest.raises(ValueError, match="API key must not be empty"):
        native.ExtendedHttpClient(api_key=" ", timeout=2)
    with pytest.raises(ValueError, match="API key must not be empty"):
        native.ExtendedPrivateWebSocketClient(api_key=" ", timeout=2)
    public = native.ExtendedPublicWebSocketClient(timeout=2)
    with pytest.raises(ValueError, match="depth must be 1"):
        await public.subscribe_orderbook(None, 2)
    with pytest.raises(ValueError, match="unsupported Extended candle interval"):
        await public.subscribe_candles("BTC-USD", "trades", "1m")
