"""Regression coverage for Bitget Savings and Earn wrappers."""

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    def private_request_json(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append((method_name, params))
        return 200, {}, {"code": "00000", "data": {}}


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    async def private_request_json_async(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append((method_name, params))
        return 200, {}, {"code": "00000", "data": {}}


def test_sync_bitget_earn_wrappers_forward_official_fields() -> None:
    """Sync wrappers preserve Savings read and mutation parameters."""
    from dcex.bitget.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_earn_account_assets("USDT")
    client.get_savings_products("USDT", filter="available_and_held")
    client.get_savings_assets("flexible", limit=10)
    client.get_savings_records("fixed", orderType="pay_interest", limit=20)
    client.subscribe_savings("product", "flexible", "1")
    client.redeem_savings("product", "fixed", "1", orderId="asset-order")
    client.get_elite_earn_products()
    client.subscribe_elite_earn("product-sub", "1", paymentAccount="unified")
    client.redeem_elite_earn(
        "product", "product-sub", "standard", "1", "unified", advancedSettle="no"
    )
    client.get_elite_earn_records("interest", limit=20)

    assert native.calls[1] == (
        "get_savings_products",
        [("coin", "USDT"), ("filter", "available_and_held")],
    )
    assert native.calls[4] == (
        "subscribe_savings",
        [("productId", "product"), ("periodType", "flexible"), ("amount", "1")],
    )
    assert native.calls[7] == (
        "subscribe_elite_earn",
        [("productSubId", "product-sub"), ("amount", "1"), ("paymentAccount", "unified")],
    )


@pytest.mark.asyncio
async def test_async_bitget_earn_wrappers_forward_official_fields() -> None:
    """Async wrappers preserve Savings result and redemption fields."""
    from dcex.async_support.bitget.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_savings_account()
    await client.get_savings_subscription_info("product", "flexible")
    await client.get_savings_subscription_result("order", "flexible")
    await client.get_savings_redemption_result("order", "fixed")
    await client.get_elite_earn_subscription_info("product")
    await client.get_elite_earn_subscription_result("order")
    await client.get_elite_earn_redemption_info("product")
    await client.get_elite_earn_assets()

    assert native.calls[1] == (
        "get_savings_subscription_info",
        [("productId", "product"), ("periodType", "flexible")],
    )
    assert native.calls[3] == (
        "get_savings_redemption_result",
        [("orderId", "order"), ("periodType", "fixed")],
    )
    assert native.calls[4] == (
        "get_elite_earn_subscription_info",
        [("productId", "product")],
    )
