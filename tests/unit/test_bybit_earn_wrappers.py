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
    client.get_advanced_earn_products("DualAssets", coin="BTC")
    client.get_advanced_earn_product_quote("DualAssets", "product-1")
    client.get_advanced_earn_positions("SmartLeverage", limit=20)
    client.get_advanced_earn_orders("DoubleWin", limit=10)
    client.place_advanced_earn_order(
        "DiscountBuy",
        "product-2",
        "Stake",
        "FUND",
        "discount-1",
        amount="10",
        coin="USDT",
        discountBuyExtra={"initialPrice": "1", "purchasePrice": "0.9"},
    )
    client.get_liquidity_mining_products(baseCoin="BTC")
    client.get_liquidity_mining_orders(orderType="AddLiquidity", limit=5)
    client.add_liquidity_mining(
        "36", "lm-1", quoteAmount="200", quoteAccountType="FUND", leverage="2"
    )
    client.remove_liquidity_mining("36", "lm-2", "5001", removeRate=50)
    client.get_fixed_earn_products(coin="USDT")
    client.get_fixed_earn_orders(category="FundPool", productId="27", limit=10)
    client.place_fixed_earn_order(
        "27", "FundPool", "USDT", "100", "FUND", "fixed-1", autoInvest=True
    )
    client.get_hold_to_earn_products()
    client.get_hold_to_earn_yield_history(limit=20)
    client.get_byusdt_product()
    client.get_byusdt_apr_history(2)
    client.get_byusdt_orders(orderType="Mint", limit=5)
    client.place_byusdt_order("Mint", "100", "FlexibleSaving", "byusdt-1")
    client.get_rwa_earn_products(coin="USDC")
    client.get_rwa_earn_nav_chart(1001, startTime=1, endTime=2)
    client.get_rwa_earn_orders(productId=1001, limit=5)
    client.place_rwa_earn_order(1001, "Stake", "USDC", "rwa-1", stakeAmount="10")
    client.get_earn_apr_history("FlexibleSaving", "430")
    client.get_earn_coupons("FlexibleSaving")
    client.set_earn_auto_reinvest(8, 326, 1)

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
    assert native.calls[4] == (
        "public",
        "get_advanced_earn_products",
        [("category", "DualAssets"), ("coin", "BTC")],
    )
    assert native.calls[5][1] == "get_advanced_earn_product_quote"
    assert native.calls[6][1] == "get_advanced_earn_positions"
    assert native.calls[8][1] == "place_advanced_earn_order"
    assert (
        "discountBuyExtra",
        '{"initialPrice":"1","purchasePrice":"0.9"}',
    ) in native.calls[8][2]
    assert native.calls[9] == (
        "public",
        "get_liquidity_mining_products",
        [("baseCoin", "BTC")],
    )
    assert native.calls[10][1] == "get_liquidity_mining_orders"
    assert ("quoteAmount", "200") in native.calls[11][2]
    assert ("removeRate", "50") in native.calls[12][2]
    assert native.calls[13] == (
        "public",
        "get_fixed_earn_products",
        [("coin", "USDT")],
    )
    assert ("productId", "27") in native.calls[14][2]
    assert ("autoInvest", "true") in native.calls[15][2]
    assert native.calls[16] == ("public", "get_hold_to_earn_products", [])
    assert native.calls[17] == (
        "private",
        "get_hold_to_earn_yield_history",
        [("limit", "20")],
    )
    assert native.calls[18] == ("public", "get_byusdt_product", [])
    assert native.calls[19][2] == [("range", "2")]
    assert ("orderType", "Mint") in native.calls[20][2]
    assert ("accountType", "FlexibleSaving") in native.calls[21][2]
    assert native.calls[22] == (
        "public",
        "get_rwa_earn_products",
        [("coin", "USDC")],
    )
    assert ("productId", "1001") in native.calls[23][2]
    assert ("limit", "5") in native.calls[24][2]
    assert ("stakeAmount", "10") in native.calls[25][2]
    assert native.calls[26][1] == "get_earn_apr_history"
    assert native.calls[27][2] == [("category", "FlexibleSaving")]
    assert ("autoReinvest", "1") in native.calls[28][2]


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
    await client.get_advanced_earn_products("SmartLeverage", duration="3d")
    await client.get_advanced_earn_redeem_estimates("SmartLeverage", "1,2")
    await client.get_double_win_leverage("1", "100", "90", "110")
    await client.get_liquidity_mining_products(quoteCoin="USDT")
    await client.get_liquidity_mining_positions(baseCoin="ETH")
    await client.reinvest_liquidity_mining("5", "lm-3", "1498", leverage="1")
    await client.get_fixed_earn_positions(category="FixedTermSaving")
    await client.set_fixed_earn_auto_invest("27", "FundPool", "42", "Enable")
    await client.get_hold_to_earn_products()
    await client.get_hold_to_earn_yield_history(limit=10)
    await client.get_byusdt_position()
    await client.get_byusdt_daily_yield(limit=5)
    await client.get_rwa_earn_products(coin="USDC")
    await client.get_rwa_earn_positions()
    await client.get_rwa_earn_orders(orderType="Redeem", limit=2)
    await client.get_earn_apr_history("OnChain", "8")
    await client.get_earn_coupons("DualAssets")
    await client.set_earn_auto_reinvest(8, 326, 0)

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
    assert native.calls[4] == (
        "public",
        "get_advanced_earn_products",
        [("category", "SmartLeverage"), ("duration", "3d")],
    )
    assert native.calls[5][1] == "get_advanced_earn_redeem_estimates"
    assert native.calls[6][1] == "get_double_win_leverage"
    assert native.calls[7] == (
        "public",
        "get_liquidity_mining_products",
        [("quoteCoin", "USDT")],
    )
    assert native.calls[8][1] == "get_liquidity_mining_positions"
    assert ("leverage", "1") in native.calls[9][2]
    assert native.calls[10][1] == "get_fixed_earn_positions"
    assert ("status", "Enable") in native.calls[11][2]
    assert native.calls[12][1] == "get_hold_to_earn_products"
    assert native.calls[13][2] == [("limit", "10")]
    assert native.calls[14] == ("private", "get_byusdt_position", [])
    assert native.calls[15][2] == [("limit", "5")]
    assert native.calls[16] == (
        "public",
        "get_rwa_earn_products",
        [("coin", "USDC")],
    )
    assert native.calls[17] == ("private", "get_rwa_earn_positions", [])
    assert ("orderType", "Redeem") in native.calls[18][2]
    assert native.calls[19][1] == "get_earn_apr_history"
    assert native.calls[20][2] == [("category", "DualAssets")]
    assert ("autoReinvest", "0") in native.calls[21][2]
