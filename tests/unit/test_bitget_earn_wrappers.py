"""Regression coverage for Bitget Elite Earn wrappers."""

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
    """Sync wrappers preserve Elite Earn read and mutation parameters."""
    from dcex.bitget.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_elite_earn_products()
    client.subscribe_elite_earn("product-sub", "1", payment_account="unified")
    client.redeem_elite_earn(
        "product", "product-sub", "standard", "1", "unified", advanced_settle="no"
    )
    client.get_elite_earn_records("interest", limit=20)

    assert native.calls[1] == (
        "subscribe_elite_earn",
        [("productSubId", "product-sub"), ("amount", "1"), ("paymentAccount", "unified")],
    )


@pytest.mark.asyncio
async def test_async_bitget_earn_wrappers_forward_official_fields() -> None:
    """Async wrappers preserve Elite Earn result and redemption fields."""
    from dcex.async_support.bitget.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_elite_earn_subscription_info("product")
    await client.get_elite_earn_subscription_result("order")
    await client.get_elite_earn_redemption_info("product")
    await client.get_elite_earn_assets()

    assert native.calls[0] == (
        "get_elite_earn_subscription_info",
        [("productId", "product")],
    )
