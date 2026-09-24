"""Regression coverage for Kraken Earn sync and async wrappers."""

import pytest

from tests.unit.test_kraken_native_wrappers import _AsyncNative, _SyncNative


def test_sync_kraken_earn_wrappers_forward_current_fields() -> None:
    """Sync Earn wrappers preserve the official Kraken request fields."""
    from dcex.kraken._account_http import AccountHTTP

    client = object.__new__(AccountHTTP)
    native = _SyncNative()
    client._native_client = native

    client.get_earn_strategies(asset="DOT", lock_type=["instant", "bonded"], limit=10)
    client.get_earn_allocations(converted_asset="USD", hide_zero_allocations=True)
    client.allocate_earn_funds("strategy", "1.5")
    client.deallocate_earn_funds("strategy", "1.5")
    client.get_earn_allocation_status("strategy")
    client.get_earn_deallocation_status("strategy")

    calls = native.calls
    assert calls[0] == (
        "get_earn_strategies",
        [
            ("asset", "DOT"),
            ("limit", "10"),
            ("lock_type", "instant"),
            ("lock_type", "bonded"),
        ],
    )
    assert calls[1] == (
        "get_earn_allocations",
        [("converted_asset", "USD"), ("hide_zero_allocations", "true")],
    )
    assert calls[2] == (
        "allocate_earn_funds",
        [("strategy_id", "strategy"), ("amount", "1.5")],
    )


@pytest.mark.asyncio
async def test_async_kraken_earn_wrappers_forward_current_fields() -> None:
    """Async Earn wrappers preserve the official Kraken request fields."""
    from dcex.async_support.kraken._account_http import AccountHTTP

    client = object.__new__(AccountHTTP)
    native = _AsyncNative()
    client._native_client = native

    await client.get_earn_strategies(ascending=True, cursor="next")
    await client.get_earn_allocations(limit=20)
    await client.allocate_earn_funds("strategy", "2")
    await client.deallocate_earn_funds("strategy", "2")
    await client.get_earn_allocation_status("strategy")
    await client.get_earn_deallocation_status("strategy")

    calls = native.calls
    assert calls[0] == (
        "get_earn_strategies",
        [("ascending", "true"), ("cursor", "next")],
    )
    assert calls[1] == ("get_earn_allocations", [("limit", "20")])
