"""Regression coverage for OKX Savings and staking wrappers."""
# ruff: noqa: ANN001, ANN202, D103

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[tuple[str, str]]]] = []

    def private_request_json(self, method_name, params):
        self.calls.append(("private", method_name, params))
        return 200, {}, {"code": "0", "data": []}

    def public_request_json(self, method_name, params):
        self.calls.append(("public", method_name, params))
        return 200, {}, {"code": "0", "data": []}


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[tuple[str, str]]]] = []

    async def private_request_json_async(self, method_name, params):
        self.calls.append(("private", method_name, params))
        return 200, {}, {"code": "0", "data": []}

    async def public_request_json_async(self, method_name, params):
        self.calls.append(("public", method_name, params))
        return 200, {}, {"code": "0", "data": []}


def test_sync_okx_finance_wrappers_forward_official_fields() -> None:
    from dcex.okx.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_saving_balance("USDT")
    client.purchase_redeem_savings("USDT", "1", "purchase", rate="0.01")
    client.set_savings_lending_rate("USDT", "0.01")
    client.get_public_borrow_history("USDT", limit=20)
    client.set_auto_earn("USDT", "turn_on", earnType="0")
    client.purchase_staking("product", [{"ccy": "ETH", "amt": "1"}], term="30")
    client.redeem_staking("order", "defi", allowEarlyRedeem=True)
    client.purchase_eth_staking("1")
    client.cancel_eth_staking_redemption("order")
    client.get_sol_staking_apy_history(7)
    client.get_flexible_loan_borrow_currencies()
    client.get_flexible_loan_max_loan("USDT", [{"ccy": "BTC", "amt": "0.1"}])
    client.adjust_flexible_loan_collateral("add", "BTC", "0.1")
    client.borrow_flexible_loan(
        [{"ccy": "USDT", "amt": "10"}],
        "client-1",
        collateralData=[{"ccy": "BTC", "amt": "0.1"}],
        eMode=True,
    )
    client.repay_flexible_loan("order", "USDT", "10", "client-2")
    client.get_dual_investment_currency_pairs()
    client.get_dual_investment_products("BTC", quoteCcy="USDT", optType="C")
    client.request_dual_investment_quote("product", "10", "USDT")
    client.trade_dual_investment("quote")
    client.request_dual_investment_redeem_quote("order")
    client.redeem_dual_investment("order", "quote")
    client.get_dual_investment_order_status("order")

    assert native.calls[1] == (
        "private",
        "purchase_redeem_savings",
        [("ccy", "USDT"), ("amt", "1"), ("side", "purchase"), ("rate", "0.01")],
    )
    assert native.calls[5][2][1] == ("investData", '[{"ccy":"ETH","amt":"1"}]')
    assert native.calls[6][2][-1] == ("allowEarlyRedeem", "true")
    assert native.calls[9][0] == "public"
    assert native.calls[11][2][1] == (
        "supCollateral",
        '[{"ccy":"BTC","amt":"0.1"}]',
    )
    assert native.calls[13][2][-1] == ("eMode", "true")
    assert native.calls[16][0] == "private"
    assert native.calls[17][2] == [
        ("productId", "product"),
        ("notionalSz", "10"),
        ("notionalCcy", "USDT"),
    ]


@pytest.mark.asyncio
async def test_async_okx_finance_wrappers_forward_official_fields() -> None:
    from dcex.async_support.okx.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_savings_lending_history("USDT", limit=10)
    await client.get_public_borrow_info("USDT")
    await client.get_staking_offers(protocolType="defi", ccy="ETH")
    await client.get_active_staking_orders(state="8")
    await client.get_staking_order_history(limit=20)
    await client.get_eth_staking_product_info()
    await client.get_eth_staking_balance()
    await client.get_eth_staking_history("purchase", limit=20)
    await client.get_sol_staking_product_info()
    await client.get_sol_staking_balance()
    await client.get_sol_staking_history("redeem", limit=20)
    await client.get_flexible_loan_collateral_assets("BTC")
    await client.get_flexible_loan_max_collateral_redeem("BTC")
    await client.get_flexible_loan_info("order")
    await client.get_flexible_loan_history("borrow", limit=20)
    await client.get_flexible_loan_interest_accrued("USDT", limit=20)
    await client.get_flexible_loan_emode_info()
    await client.get_dual_investment_order_history(productId="product", state="filled", limit=20)

    assert native.calls[0][1] == "get_savings_lending_history"
    assert native.calls[1][0] == "public"
    assert native.calls[2][2] == [("protocolType", "defi"), ("ccy", "ETH")]
    assert native.calls[-1] == (
        "private",
        "get_dual_investment_order_history",
        [("productId", "product"), ("state", "filled"), ("limit", "20")],
    )
