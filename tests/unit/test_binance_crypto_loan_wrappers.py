"""Regression coverage for Binance Crypto Loan sync and async wrappers."""
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
    client.check_flexible_loan_collateral_repay_rate("USDT", "BTC")
    client.adjust_flexible_loan_ltv("USDT", "BTC", "0.01", "ADDITIONAL")
    client.borrow_flexible_loan("USDT", "BTC", loanAmount="10")
    client.repay_flexible_loan("USDT", "BTC", "10", fullRepayment=True)
    client.get_flexible_loan_assets("USDT")
    client.get_flexible_loan_collateral_assets("BTC")
    client.get_flexible_loan_interest_rate_history("USDT", limit=10)
    client.get_flexible_loan_ongoing_orders(loanCoin="USDT", limit=10)
    client.get_flexible_loan_borrow_history(loanCoin="USDT", limit=10)
    client.get_flexible_loan_repayment_history(loanCoin="USDT", limit=10)
    client.get_flexible_loan_ltv_adjustment_history(loanCoin="USDT", limit=10)
    client.get_flexible_loan_liquidation_history(loanCoin="USDT", limit=10)
    client.get_crypto_loan_income_history(asset="USDT", type_="borrowIn", limit=10)
    client.get_stable_loan_borrow_history(loanCoin="USDT", limit=10)
    client.get_stable_loan_repayment_history(loanCoin="USDT", limit=10)
    client.get_stable_loan_ltv_adjustment_history(loanCoin="USDT", limit=10)


async def _exercise_async(client: Any) -> None:  # noqa: ANN401
    await client.check_flexible_loan_collateral_repay_rate("USDT", "BTC")
    await client.adjust_flexible_loan_ltv("USDT", "BTC", "0.01", "ADDITIONAL")
    await client.borrow_flexible_loan("USDT", "BTC", loanAmount="10")
    await client.repay_flexible_loan("USDT", "BTC", "10", fullRepayment=True)
    await client.get_flexible_loan_assets("USDT")
    await client.get_flexible_loan_collateral_assets("BTC")
    await client.get_flexible_loan_interest_rate_history("USDT", limit=10)
    await client.get_flexible_loan_ongoing_orders(loanCoin="USDT", limit=10)
    await client.get_flexible_loan_borrow_history(loanCoin="USDT", limit=10)
    await client.get_flexible_loan_repayment_history(loanCoin="USDT", limit=10)
    await client.get_flexible_loan_ltv_adjustment_history(loanCoin="USDT", limit=10)
    await client.get_flexible_loan_liquidation_history(loanCoin="USDT", limit=10)
    await client.get_crypto_loan_income_history(asset="USDT", type_="borrowIn", limit=10)
    await client.get_stable_loan_borrow_history(loanCoin="USDT", limit=10)
    await client.get_stable_loan_repayment_history(loanCoin="USDT", limit=10)
    await client.get_stable_loan_ltv_adjustment_history(loanCoin="USDT", limit=10)


def _assert_calls(calls: list[dict[str, Any]]) -> None:
    assert len(calls) == 16
    assert calls[0]["path"] == "check_flexible_loan_collateral_repay_rate"
    assert calls[2]["path"] == "borrow_flexible_loan"
    assert dict(calls[2]["query"])["loanAmount"] == "10"
    assert dict(calls[3]["query"])["fullRepayment"] == "true"
    assert dict(calls[12]["query"])["type"] == "borrowIn"
    assert all("self" not in dict(call["query"]) for call in calls)


def test_sync_binance_crypto_loan_wrappers_forward_current_fields() -> None:
    client = _client_class("sync", "binance")(**_client_kwargs("binance"))
    calls = _wire_sync(client)
    _exercise_sync(client)
    _assert_calls(calls)


@pytest.mark.asyncio
async def test_async_binance_crypto_loan_wrappers_forward_current_fields() -> None:
    client = _client_class("async", "binance")(**_client_kwargs("binance"))
    calls = _wire_async(client)
    await _exercise_async(client)
    _assert_calls(calls)
