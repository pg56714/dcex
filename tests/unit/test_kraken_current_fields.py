"""Regression coverage for current Kraken REST parameter surfaces."""
# ruff: noqa: D103

from __future__ import annotations

import inspect

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)

CURRENT_FIELDS = {
    "get_spot_assets": {"asset", "aclass", "assetVersion"},
    "get_spot_asset_pairs": {
        "assetVersion",
        "pair",
        "aclass_base",
        "info",
        "country_code",
        "execution_venue",
    },
    "get_spot_ticker": {"product_symbol", "pair", "assetVersion", "asset_class"},
    "get_spot_orderbook": {"product_symbol", "assetVersion", "count", "asset_class"},
    "get_spot_public_trades": {
        "product_symbol",
        "assetVersion",
        "since",
        "count",
        "asset_class",
    },
    "get_spot_kline": {
        "product_symbol",
        "assetVersion",
        "interval",
        "since",
        "asset_class",
    },
    "get_spot_spread": {"product_symbol", "assetVersion", "since", "asset_class"},
    "get_spot_trade_balance": {"asset", "rebase_multiplier"},
    "get_spot_ledgers": {"rebase_multiplier"},
    "get_spot_trade_volume": {"fee_info", "fee_schedule", "rebase_multiplier"},
    "get_spot_open_orders": {"cl_ord_id", "rebase_multiplier"},
    "get_spot_closed_orders": {
        "cl_ord_id",
        "consolidate_taker",
        "without_count",
        "rebase_multiplier",
    },
    "get_spot_orders": {"consolidate_taker", "rebase_multiplier"},
    "get_spot_trade_history": {"ledgers", "rebase_multiplier"},
    "cancel_futures_order": {"order_id", "cliOrdId", "processBefore"},
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_kraken_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "kraken")
    async_client = _client_class("async", "kraken")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


def test_kraken_websocket_token_has_no_undocumented_permissions_field() -> None:
    sync_client = _client_class("sync", "kraken")
    async_client = _client_class("async", "kraken")
    assert set(inspect.signature(sync_client.get_spot_websocket_token).parameters) == {"self"}
    assert set(inspect.signature(async_client.get_spot_websocket_token).parameters) == {"self"}


def test_sync_kraken_forwards_current_market_and_account_fields() -> None:
    market = _client_class("sync", "kraken")(**_client_kwargs("kraken"))
    calls = _wire_sync(market)

    market.get_spot_public_trades(
        "BTC-USD-SPOT",
        since="123",
        count=50,
        assetVersion=1,
        asset_class="currency",
    )

    assert dict(calls[0]["query"]) == {
        "product_symbol": "BTC-USD-SPOT",
        "since": "123",
        "count": "50",
        "assetVersion": "1",
        "asset_class": "currency",
    }


@pytest.mark.asyncio
async def test_async_kraken_forwards_current_order_history_fields() -> None:
    trade = _client_class("async", "kraken")(**_client_kwargs("kraken"))
    calls = _wire_async(trade)

    await trade.get_spot_closed_orders(
        cl_ord_id="client-id",
        consolidate_taker=True,
        without_count=False,
        rebase_multiplier="1",
    )

    assert dict(calls[0]["query"]) == {
        "cl_ord_id": "client-id",
        "consolidate_taker": "true",
        "without_count": "false",
        "rebase_multiplier": "1",
    }


def test_kraken_spot_order_rejects_mutually_exclusive_client_ids() -> None:
    trade = _client_class("sync", "kraken")(**_client_kwargs("kraken"))

    with pytest.raises(ValueError, match="mutually exclusive"):
        trade.place_spot_order(
            "BTC-USD-SPOT",
            "buy",
            "limit",
            "0.001",
            price="100",
            userref=7,
            cl_ord_id="client-id",
        )


def test_kraken_cancel_requires_exactly_one_spot_identifier() -> None:
    trade = _client_class("sync", "kraken")(**_client_kwargs("kraken"))

    with pytest.raises(ValueError, match="exactly one"):
        trade.cancel_spot_order(txid="order-id", cl_ord_id="client-id")


def test_kraken_cancel_requires_exactly_one_futures_identifier() -> None:
    trade = _client_class("sync", "kraken")(**_client_kwargs("kraken"))

    with pytest.raises(ValueError, match="exactly one"):
        trade.cancel_futures_order(order_id="order-id", cliOrdId="client-id")
