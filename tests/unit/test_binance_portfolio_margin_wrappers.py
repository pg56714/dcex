"""Offline sync and async Portfolio Margin wrapper parameter coverage."""

from __future__ import annotations

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)


def _assert_calls(calls: list[dict[str, object]]) -> None:
    assert [call["path"] for call in calls] == [
        "set_pm_um_leverage",
        "set_pm_cm_position_mode",
        "modify_pm_um_order",
        "place_pm_cm_conditional_order",
        "place_pm_margin_oco",
        "borrow_pm_margin",
        "get_pm_um_algo_order_history",
    ]
    leverage = dict(calls[0]["query"])
    mode = dict(calls[1]["query"])
    modify = dict(calls[2]["query"])
    conditional = dict(calls[3]["query"])
    oco = dict(calls[4]["query"])
    borrow = dict(calls[5]["query"])
    assert leverage["leverage"] == "10"
    assert mode["dualSidePosition"] == "true"
    assert modify["orderId"] == "123"
    assert modify["quantity"] == "0.02"
    assert conditional["strategyType"] == "STOP_MARKET"
    assert conditional["stopPrice"] == "39000"
    assert oco["stopPrice"] == "90"
    assert borrow["asset"] == "USDT"
    assert borrow["amount"] == "100"
    history = dict(calls[6]["query"])
    assert history["algoId"] == "5"
    assert "page" not in history


def test_sync_portfolio_margin_parameters() -> None:
    """Ensure synchronous PM wrappers forward required fields."""
    client = _client_class("sync", "binance")(**_client_kwargs("binance"))
    calls = _wire_sync(client)
    client.set_pm_um_leverage("BTCUSDT", 10)
    client.set_pm_cm_position_mode(True)
    client.modify_pm_um_order("BTCUSDT", "BUY", 123, "0.02", "40000")
    client.place_pm_cm_conditional_order(
        "BTCUSD_PERP", "SELL", "STOP_MARKET", quantity="1", stop_price="39000"
    )
    client.place_pm_margin_oco("LTCBTC", "SELL", "1", "100", "90")
    client.borrow_pm_margin("USDT", "100")
    client.get_pm_um_algo_order_history("BTCUSDT", algo_id=5)
    _assert_calls(calls)


@pytest.mark.asyncio
async def test_async_portfolio_margin_parameters() -> None:
    """Ensure asynchronous PM wrappers forward required fields."""
    client = _client_class("async", "binance")(**_client_kwargs("binance"))
    calls = _wire_async(client)
    await client.set_pm_um_leverage("BTCUSDT", 10)
    await client.set_pm_cm_position_mode(True)
    await client.modify_pm_um_order("BTCUSDT", "BUY", 123, "0.02", "40000")
    await client.place_pm_cm_conditional_order(
        "BTCUSD_PERP", "SELL", "STOP_MARKET", quantity="1", stop_price="39000"
    )
    await client.place_pm_margin_oco("LTCBTC", "SELL", "1", "100", "90")
    await client.borrow_pm_margin("USDT", "100")
    await client.get_pm_um_algo_order_history("BTCUSDT", algo_id=5)
    _assert_calls(calls)
