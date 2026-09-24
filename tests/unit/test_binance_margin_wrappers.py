"""Regression coverage for Binance Margin sync and async wrappers."""
# ruff: noqa: D103

from __future__ import annotations

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)


def _exercise_sync(client: object) -> None:
    client.get_all_margin_assets()
    client.get_all_cross_margin_pairs()
    client.get_all_isolated_margin_symbols()
    client.get_margin_price_index("BTC-USDT-SPOT")
    client.get_cross_margin_account()
    client.get_isolated_margin_account(["BTC-USDT-SPOT"])
    client.borrow_margin_asset("USDT", "1")
    client.repay_margin_asset("USDT", "1", isIsolated=True, product_symbol="BTC-USDT-SPOT")
    client.get_margin_borrow_repay_records("BORROW", asset="USDT", size=10)
    client.get_margin_interest_history(asset="USDT", size=10)
    client.get_margin_max_borrowable("USDT")
    client.get_margin_max_transferable("USDT")
    client.place_margin_order(
        "BTC-USDT-SPOT",
        "BUY",
        "LIMIT",
        quantity="0.001",
        price="1",
        timeInForce="GTC",
        sideEffectType="AUTO_BORROW_REPAY",
        autoRepayAtCancel=True,
    )
    client.cancel_margin_order("BTC-USDT-SPOT", orderId=1)
    client.get_margin_order("BTC-USDT-SPOT", orderId=1)
    client.get_open_margin_orders(product_symbol="BTC-USDT-SPOT")
    client.cancel_all_open_margin_orders("BTC-USDT-SPOT")
    client.get_all_margin_orders("BTC-USDT-SPOT", limit=10)
    client.get_margin_account_trades("BTC-USDT-SPOT", limit=10)


async def _exercise_async(client: object) -> None:
    await client.get_all_margin_assets()
    await client.get_all_cross_margin_pairs()
    await client.get_all_isolated_margin_symbols()
    await client.get_margin_price_index("BTC-USDT-SPOT")
    await client.get_cross_margin_account()
    await client.get_isolated_margin_account(["BTC-USDT-SPOT"])
    await client.borrow_margin_asset("USDT", "1")
    await client.repay_margin_asset("USDT", "1", isIsolated=True, product_symbol="BTC-USDT-SPOT")
    await client.get_margin_borrow_repay_records("BORROW", asset="USDT", size=10)
    await client.get_margin_interest_history(asset="USDT", size=10)
    await client.get_margin_max_borrowable("USDT")
    await client.get_margin_max_transferable("USDT")
    await client.place_margin_order(
        "BTC-USDT-SPOT",
        "BUY",
        "LIMIT",
        quantity="0.001",
        price="1",
        timeInForce="GTC",
        sideEffectType="AUTO_BORROW_REPAY",
        autoRepayAtCancel=True,
    )
    await client.cancel_margin_order("BTC-USDT-SPOT", orderId=1)
    await client.get_margin_order("BTC-USDT-SPOT", orderId=1)
    await client.get_open_margin_orders(product_symbol="BTC-USDT-SPOT")
    await client.cancel_all_open_margin_orders("BTC-USDT-SPOT")
    await client.get_all_margin_orders("BTC-USDT-SPOT", limit=10)
    await client.get_margin_account_trades("BTC-USDT-SPOT", limit=10)


def _assert_calls(calls: list[dict[str, object]]) -> None:
    assert [call["path"] for call in calls] == [
        "get_all_margin_assets",
        "get_all_cross_margin_pairs",
        "get_all_isolated_margin_symbols",
        "get_margin_price_index",
        "get_cross_margin_account",
        "get_isolated_margin_account",
        "margin_borrow_repay",
        "margin_borrow_repay",
        "get_margin_borrow_repay_records",
        "get_margin_interest_history",
        "get_margin_max_borrowable",
        "get_margin_max_transferable",
        "place_margin_order",
        "cancel_margin_order",
        "get_margin_order",
        "get_open_margin_orders",
        "cancel_all_open_margin_orders",
        "get_all_margin_orders",
        "get_margin_account_trades",
    ]
    borrow = dict(calls[6]["query"])
    repay = dict(calls[7]["query"])
    order = dict(calls[12]["query"])
    assert borrow["type"] == "BORROW"
    assert borrow["isIsolated"] == "false"
    assert repay["type"] == "REPAY"
    assert repay["isIsolated"] == "true"
    assert order["sideEffectType"] == "AUTO_BORROW_REPAY"
    assert order["autoRepayAtCancel"] == "true"


def test_sync_binance_margin_wrappers_forward_current_fields() -> None:
    client = _client_class("sync", "binance")(**_client_kwargs("binance"))
    calls = _wire_sync(client)
    _exercise_sync(client)
    _assert_calls(calls)


@pytest.mark.asyncio
async def test_async_binance_margin_wrappers_forward_current_fields() -> None:
    client = _client_class("async", "binance")(**_client_kwargs("binance"))
    calls = _wire_async(client)
    await _exercise_async(client)
    _assert_calls(calls)
