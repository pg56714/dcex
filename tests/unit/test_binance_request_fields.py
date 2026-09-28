"""Regression coverage for current Binance Spot request fields."""
# ruff: noqa: D103

from __future__ import annotations

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)


def test_sync_binance_current_market_and_account_fields_are_forwarded() -> None:
    client = _client_class("sync", "binance")(**_client_kwargs("binance"))
    calls = _wire_sync(client)

    client.get_spot_exchange_info(
        permissions=["SPOT", "MARGIN"],
        showPermissionSets=False,
        symbolStatus="TRADING",
    )
    client.get_spot_orderbook("BTC-USDT-SPOT", limit=100, symbolStatus="TRADING")
    client.get_spot_trades("BTC-USDT-SPOT", limit=100, symbolStatus="TRADING")
    client.get_klines(
        "BTC-USDT-SPOT",
        "1m",
        start_time=1,
        end_time=2,
        time_zone="8",
        limit=10,
    )
    client.get_account_balance("spot", omitZeroBalances=True)
    client.cancel_order(
        "BTC-USDT-SPOT",
        orderId=1,
        newClientOrderId="cancel-1",
        cancelRestrictions="ONLY_NEW",
    )
    client.get_account_trades("BTC-USDT-SWAP", orderId=2)
    client.get_future_position()

    assert calls[0]["query"] == [
        ("permissions", "SPOT"),
        ("permissions", "MARGIN"),
        ("showPermissionSets", "false"),
        ("symbolStatus", "TRADING"),
    ]
    assert dict(calls[1]["query"])["symbolStatus"] == "TRADING"
    assert dict(calls[2]["query"])["symbolStatus"] == "TRADING"
    assert {"end_time", "time_zone"} <= set(dict(calls[3]["query"]))
    assert dict(calls[4]["query"])["omitZeroBalances"] == "true"
    assert {"newClientOrderId", "cancelRestrictions"} <= set(dict(calls[5]["query"]))
    assert dict(calls[6]["query"])["orderId"] == "2"
    assert calls[7]["query"] == []


@pytest.mark.asyncio
async def test_async_binance_current_market_and_account_fields_are_forwarded() -> None:
    client = _client_class("async", "binance")(**_client_kwargs("binance"))
    calls = _wire_async(client)

    await client.get_spot_exchange_info(
        permissions=["SPOT", "MARGIN"],
        showPermissionSets=False,
        symbolStatus="TRADING",
    )
    await client.get_spot_orderbook("BTC-USDT-SPOT", limit=100, symbolStatus="TRADING")
    await client.get_spot_trades("BTC-USDT-SPOT", limit=100, symbolStatus="TRADING")
    await client.get_klines(
        "BTC-USDT-SPOT",
        "1m",
        start_time=1,
        end_time=2,
        time_zone="8",
        limit=10,
    )
    await client.get_account_balance("spot", omitZeroBalances=True)
    await client.cancel_order(
        "BTC-USDT-SPOT",
        orderId=1,
        newClientOrderId="cancel-1",
        cancelRestrictions="ONLY_NEW",
    )
    await client.get_account_trades("BTC-USDT-SWAP", orderId=2)
    await client.get_future_position()

    assert calls[0]["query"] == [
        ("permissions", "SPOT"),
        ("permissions", "MARGIN"),
        ("showPermissionSets", "false"),
        ("symbolStatus", "TRADING"),
    ]
    assert dict(calls[1]["query"])["symbolStatus"] == "TRADING"
    assert dict(calls[2]["query"])["symbolStatus"] == "TRADING"
    assert {"end_time", "time_zone"} <= set(dict(calls[3]["query"]))
    assert dict(calls[4]["query"])["omitZeroBalances"] == "true"
    assert {"newClientOrderId", "cancelRestrictions"} <= set(dict(calls[5]["query"]))
    assert dict(calls[6]["query"])["orderId"] == "2"
    assert calls[7]["query"] == []
