"""Regression coverage for Binance Simple Earn sync and async wrappers."""
# ruff: noqa: D103

from __future__ import annotations

from typing import Any

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)


def _exercise_sync(client: Any) -> None:  # noqa: ANN401
    client.get_simple_earn_account()
    client.get_flexible_earn_products(asset="USDT", size=10)
    client.get_locked_earn_products(asset="USDT", size=10)
    client.get_flexible_earn_positions(asset="USDT", size=10)
    client.get_locked_earn_positions(asset="USDT", size=10)
    client.subscribe_flexible_earn("USDT001", "1", autoSubscribe=True, sourceAccount="SPOT")
    client.subscribe_locked_earn("project-1", "1", redeemTo="SPOT")
    client.redeem_flexible_earn("USDT001", amount="1")
    client.redeem_flexible_earn("USDT001", redeemAll=True)
    client.redeem_locked_earn("position-1")
    client.get_flexible_earn_subscription_history(asset="USDT", size=10)
    client.get_locked_earn_subscription_history(asset="USDT", size=10)
    client.get_flexible_earn_redemption_history(asset="USDT", size=10)
    client.get_locked_earn_redemption_history(asset="USDT", size=10)
    client.get_flexible_earn_rewards_history(asset="USDT", type_="ALL", size=10)
    client.get_locked_earn_rewards_history(asset="USDT", size=10)


async def _exercise_async(client: Any) -> None:  # noqa: ANN401
    await client.get_simple_earn_account()
    await client.get_flexible_earn_products(asset="USDT", size=10)
    await client.get_locked_earn_products(asset="USDT", size=10)
    await client.get_flexible_earn_positions(asset="USDT", size=10)
    await client.get_locked_earn_positions(asset="USDT", size=10)
    await client.subscribe_flexible_earn("USDT001", "1", autoSubscribe=True, sourceAccount="SPOT")
    await client.subscribe_locked_earn("project-1", "1", redeemTo="SPOT")
    await client.redeem_flexible_earn("USDT001", amount="1")
    await client.redeem_flexible_earn("USDT001", redeemAll=True)
    await client.redeem_locked_earn("position-1")
    await client.get_flexible_earn_subscription_history(asset="USDT", size=10)
    await client.get_locked_earn_subscription_history(asset="USDT", size=10)
    await client.get_flexible_earn_redemption_history(asset="USDT", size=10)
    await client.get_locked_earn_redemption_history(asset="USDT", size=10)
    await client.get_flexible_earn_rewards_history(asset="USDT", type_="ALL", size=10)
    await client.get_locked_earn_rewards_history(asset="USDT", size=10)


def _assert_calls(calls: list[dict[str, Any]]) -> None:
    assert [call["path"] for call in calls] == [
        "get_simple_earn_account",
        "get_flexible_earn_products",
        "get_locked_earn_products",
        "get_flexible_earn_positions",
        "get_locked_earn_positions",
        "subscribe_flexible_earn",
        "subscribe_locked_earn",
        "redeem_flexible_earn",
        "redeem_flexible_earn",
        "redeem_locked_earn",
        "get_flexible_earn_subscription_history",
        "get_locked_earn_subscription_history",
        "get_flexible_earn_redemption_history",
        "get_locked_earn_redemption_history",
        "get_flexible_earn_rewards_history",
        "get_locked_earn_rewards_history",
    ]
    assert "self" not in dict(calls[10]["query"])
    assert dict(calls[5]["query"])["autoSubscribe"] == "true"
    assert dict(calls[8]["query"])["redeemAll"] == "true"
    assert dict(calls[14]["query"])["type"] == "ALL"


def test_sync_binance_simple_earn_wrappers_forward_current_fields() -> None:
    client = _client_class("sync", "binance")(**_client_kwargs("binance"))
    calls = _wire_sync(client)
    _exercise_sync(client)
    _assert_calls(calls)


@pytest.mark.asyncio
async def test_async_binance_simple_earn_wrappers_forward_current_fields() -> None:
    client = _client_class("async", "binance")(**_client_kwargs("binance"))
    calls = _wire_async(client)
    await _exercise_async(client)
    _assert_calls(calls)
