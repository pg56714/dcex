"""Regression coverage for Bybit Earn sync and async wrappers."""

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[tuple[str, str]]]] = []

    def public_request_json(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(("public", method_name, params))
        return 200, {}, {"retCode": 0, "result": {}}

    def private_request_json(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(("private", method_name, params))
        return 200, {}, {"retCode": 0, "result": {}}


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[tuple[str, str]]]] = []

    async def public_request_json_async(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(("public", method_name, params))
        return 200, {}, {"retCode": 0, "result": {}}

    async def private_request_json_async(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(("private", method_name, params))
        return 200, {}, {"retCode": 0, "result": {}}


def test_sync_bybit_earn_wrappers_forward_official_fields() -> None:
    """Sync wrappers preserve public, read-only, and mutation parameters."""
    from dcex.bybit.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_earn_products("FlexibleSaving", coin="USDT")
    client.get_earn_positions("FlexibleSaving", coin="USDT")
    client.get_earn_order_history("FlexibleSaving", limit=20)
    client.place_earn_order(
        "FlexibleSaving",
        "Stake",
        "FUND",
        "1",
        "USDT",
        "430",
        "earn-1",
        interestCard={"awardId": 1, "specCode": "bonus"},
    )

    assert native.calls[0] == (
        "public",
        "get_earn_products",
        [("category", "FlexibleSaving"), ("coin", "USDT")],
    )
    assert native.calls[1] == (
        "private",
        "get_earn_positions",
        [("category", "FlexibleSaving"), ("coin", "USDT")],
    )
    assert native.calls[3][1] == "place_earn_order"
    assert ("interestCard", '{"awardId":1,"specCode":"bonus"}') in native.calls[3][2]


@pytest.mark.asyncio
async def test_async_bybit_earn_wrappers_forward_official_fields() -> None:
    """Async wrappers preserve product, position, and yield parameters."""
    from dcex.async_support.bybit.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_earn_products("OnChain", coin="ETH")
    await client.get_earn_positions("OnChain", productId="123")
    await client.get_earn_yield_history("FlexibleSaving", limit=50)
    await client.get_earn_hourly_yield_history(productId="430")

    assert native.calls[0] == (
        "public",
        "get_earn_products",
        [("category", "OnChain"), ("coin", "ETH")],
    )
    assert native.calls[2] == (
        "private",
        "get_earn_yield_history",
        [("category", "FlexibleSaving"), ("limit", "50")],
    )
    assert native.calls[3] == (
        "private",
        "get_earn_hourly_yield_history",
        [("category", "FlexibleSaving"), ("productId", "430")],
    )
