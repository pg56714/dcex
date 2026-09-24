"""Regression coverage for Binance Sub Account sync and async wrappers."""
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
    client.get_subaccounts(limit=10)
    client.get_subaccount_status()
    client.get_subaccount_transaction_statistics("sub@example.com")
    client.get_subaccount_futures_position_risk("sub@example.com")
    client.get_subaccount_futures_account("sub@example.com")
    client.get_subaccount_margin_account("sub@example.com")
    client.get_subaccount_futures_summary(limit=10)
    client.get_subaccount_margin_summary()
    client.get_subaccount_assets("sub@example.com")
    client.get_subaccount_spot_summary(size=10)
    client.transfer_subaccount_futures("sub@example.com", "USDT", "1", 1)
    client.transfer_subaccount_margin("sub@example.com", "USDT", "1", 1)
    client.get_subaccount_futures_transfer_history("sub@example.com", limit=10)
    client.transfer_between_subaccount_futures("a@example.com", "b@example.com", 1, "USDT", "1")
    client.get_subaccount_spot_transfer_history(limit=10)
    client.get_subaccount_universal_transfer_history(limit=10)
    client.transfer_between_subaccounts("SPOT", "SPOT", "USDT", "1", toEmail="sub@example.com")
    client.get_subaccount_transfer_history(asset="USDT", limit=10)
    client.transfer_subaccount_to_master("USDT", "1")
    client.transfer_subaccount_to_subaccount("sub@example.com", "USDT", "1")


async def _exercise_async(client: Any) -> None:  # noqa: ANN401
    await client.get_subaccounts(limit=10)
    await client.get_subaccount_status()
    await client.get_subaccount_transaction_statistics("sub@example.com")
    await client.get_subaccount_futures_position_risk("sub@example.com")
    await client.get_subaccount_futures_account("sub@example.com")
    await client.get_subaccount_margin_account("sub@example.com")
    await client.get_subaccount_futures_summary(limit=10)
    await client.get_subaccount_margin_summary()
    await client.get_subaccount_assets("sub@example.com")
    await client.get_subaccount_spot_summary(size=10)
    await client.transfer_subaccount_futures("sub@example.com", "USDT", "1", 1)
    await client.transfer_subaccount_margin("sub@example.com", "USDT", "1", 1)
    await client.get_subaccount_futures_transfer_history("sub@example.com", limit=10)
    await client.transfer_between_subaccount_futures(
        "a@example.com", "b@example.com", 1, "USDT", "1"
    )
    await client.get_subaccount_spot_transfer_history(limit=10)
    await client.get_subaccount_universal_transfer_history(limit=10)
    await client.transfer_between_subaccounts(
        "SPOT", "SPOT", "USDT", "1", toEmail="sub@example.com"
    )
    await client.get_subaccount_transfer_history(asset="USDT", limit=10)
    await client.transfer_subaccount_to_master("USDT", "1")
    await client.transfer_subaccount_to_subaccount("sub@example.com", "USDT", "1")


def _assert_calls(calls: list[dict[str, Any]]) -> None:
    assert len(calls) == 20
    assert calls[0]["path"] == "get_subaccounts"
    assert calls[8]["path"] == "get_subaccount_assets"
    assert calls[16]["path"] == "transfer_between_subaccounts"
    assert dict(calls[10]["query"])["type"] == "1"
    assert dict(calls[16]["query"])["toEmail"] == "sub@example.com"
    assert all("self" not in dict(call["query"]) for call in calls)


def test_sync_binance_subaccount_wrappers_forward_current_fields() -> None:
    client = _client_class("sync", "binance")(**_client_kwargs("binance"))
    calls = _wire_sync(client)
    _exercise_sync(client)
    _assert_calls(calls)


@pytest.mark.asyncio
async def test_async_binance_subaccount_wrappers_forward_current_fields() -> None:
    client = _client_class("async", "binance")(**_client_kwargs("binance"))
    calls = _wire_async(client)
    await _exercise_async(client)
    _assert_calls(calls)
