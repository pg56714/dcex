"""Regression coverage for Binance Staking sync and async wrappers."""
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
    client.get_eth_staking_account()
    client.get_eth_staking_quota()
    client.get_eth_redemption_history(size=10)
    client.get_eth_staking_history(size=10)
    client.get_wbeth_rate_history(size=10)
    client.get_wbeth_rewards_history(size=10)
    client.get_wbeth_unwrap_history(size=10)
    client.get_wbeth_wrap_history(size=10)
    client.subscribe_eth_staking("1")
    client.redeem_eth_staking("1", asset="WBETH")
    client.wrap_beth("1")
    client.get_onchain_yields_personal_quota("project-1")
    client.get_onchain_yields_products(asset="SOL", size=10)
    client.get_onchain_yields_positions(asset="SOL", size=10)
    client.get_onchain_yields_redemption_history(asset="SOL", size=10)
    client.get_onchain_yields_rewards_history(asset="SOL", size=10)
    client.preview_onchain_yields_subscription("project-1", "1", autoSubscribe=True)
    client.get_onchain_yields_subscription_history(asset="SOL", size=10)
    client.get_onchain_yields_account()
    client.subscribe_onchain_yields("project-1", "1", sourceAccount="SPOT")
    client.redeem_onchain_yields("position-1", channelId="channel-1")
    client.set_onchain_yields_auto_subscribe("position-1", True)
    client.set_onchain_yields_redeem_option("position-1", "SPOT")
    client.get_soft_staking_products(asset="BTC", size=10)
    client.get_soft_staking_rewards_history(asset="BTC", size=10)
    client.set_soft_staking(True)
    client.get_sol_staking_account()
    client.get_sol_staking_quota()
    client.get_bnsol_rate_history(size=10)
    client.get_bnsol_rewards_history(size=10)
    client.get_sol_boost_rewards_history(type="CLAIM", size=10)
    client.get_sol_redemption_history(size=10)
    client.get_sol_staking_history(size=10)
    client.get_sol_unclaimed_rewards()
    client.claim_sol_boost_rewards()
    client.subscribe_sol_staking("1")
    client.redeem_sol_staking("1")


async def _exercise_async(client: Any) -> None:  # noqa: ANN401
    await client.get_eth_staking_account()
    await client.get_eth_staking_quota()
    await client.get_eth_redemption_history(size=10)
    await client.get_eth_staking_history(size=10)
    await client.get_wbeth_rate_history(size=10)
    await client.get_wbeth_rewards_history(size=10)
    await client.get_wbeth_unwrap_history(size=10)
    await client.get_wbeth_wrap_history(size=10)
    await client.subscribe_eth_staking("1")
    await client.redeem_eth_staking("1", asset="WBETH")
    await client.wrap_beth("1")
    await client.get_onchain_yields_personal_quota("project-1")
    await client.get_onchain_yields_products(asset="SOL", size=10)
    await client.get_onchain_yields_positions(asset="SOL", size=10)
    await client.get_onchain_yields_redemption_history(asset="SOL", size=10)
    await client.get_onchain_yields_rewards_history(asset="SOL", size=10)
    await client.preview_onchain_yields_subscription("project-1", "1", autoSubscribe=True)
    await client.get_onchain_yields_subscription_history(asset="SOL", size=10)
    await client.get_onchain_yields_account()
    await client.subscribe_onchain_yields("project-1", "1", sourceAccount="SPOT")
    await client.redeem_onchain_yields("position-1", channelId="channel-1")
    await client.set_onchain_yields_auto_subscribe("position-1", True)
    await client.set_onchain_yields_redeem_option("position-1", "SPOT")
    await client.get_soft_staking_products(asset="BTC", size=10)
    await client.get_soft_staking_rewards_history(asset="BTC", size=10)
    await client.set_soft_staking(True)
    await client.get_sol_staking_account()
    await client.get_sol_staking_quota()
    await client.get_bnsol_rate_history(size=10)
    await client.get_bnsol_rewards_history(size=10)
    await client.get_sol_boost_rewards_history(type="CLAIM", size=10)
    await client.get_sol_redemption_history(size=10)
    await client.get_sol_staking_history(size=10)
    await client.get_sol_unclaimed_rewards()
    await client.claim_sol_boost_rewards()
    await client.subscribe_sol_staking("1")
    await client.redeem_sol_staking("1")


def _assert_calls(calls: list[dict[str, Any]]) -> None:
    assert len(calls) == 37
    assert calls[0]["path"] == "get_eth_staking_account"
    assert calls[18]["path"] == "get_onchain_yields_account"
    assert calls[26]["path"] == "get_sol_staking_account"
    assert dict(calls[16]["query"])["autoSubscribe"] == "true"
    assert dict(calls[25]["query"])["softStaking"] == "true"
    assert all("self" not in dict(call["query"]) for call in calls)


def test_sync_binance_staking_wrappers_forward_current_fields() -> None:
    client = _client_class("sync", "binance")(**_client_kwargs("binance"))
    calls = _wire_sync(client)
    _exercise_sync(client)
    _assert_calls(calls)


@pytest.mark.asyncio
async def test_async_binance_staking_wrappers_forward_current_fields() -> None:
    client = _client_class("async", "binance")(**_client_kwargs("binance"))
    calls = _wire_async(client)
    await _exercise_async(client)
    _assert_calls(calls)
