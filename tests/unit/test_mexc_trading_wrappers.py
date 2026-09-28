"""Offline coverage for mexc trading wrappers."""
# ruff: noqa: D103

import inspect
from unittest.mock import Mock

from dcex.async_support.bitget._account_http import AccountHTTP as AsyncBitgetAccount
from dcex.async_support.mexc._account_http import AccountHTTP as AsyncMexcAccount
from dcex.async_support.mexc._trade_http import TradeHTTP as AsyncMexcTrade
from dcex.bitget._account_http import AccountHTTP as BitgetAccount
from dcex.mexc._account_http import AccountHTTP as MexcAccount
from dcex.mexc._trade_http import TradeHTTP as MexcTrade


def test_mexc_advanced_sync_and_async_signatures_match() -> None:
    for sync_cls, async_cls, methods in (
        (
            MexcTrade,
            AsyncMexcTrade,
            (
                "amend_contract_limit_order",
                "chase_contract_limit_order",
                "get_contract_open_order_count",
                "reverse_contract_position",
                "close_all_contract_positions",
                "place_contract_trailing_order",
                "cancel_contract_trailing_order",
                "amend_contract_trailing_order",
                "get_contract_trailing_orders",
                "amend_contract_plan_order",
                "place_contract_position_tpsl",
                "cancel_contract_tpsl_orders",
                "cancel_all_contract_tpsl_orders",
                "amend_contract_limit_tpsl",
                "amend_contract_tpsl_order",
                "amend_contract_plan_tpsl",
            ),
        ),
        (
            MexcAccount,
            AsyncMexcAccount,
            (
                "change_contract_multi_asset_mode",
                "change_contract_auto_add_margin",
            ),
        ),
        (
            BitgetAccount,
            AsyncBitgetAccount,
            (
                "get_reality_orderbook",
                "get_reality_fills",
            ),
        ),
    ):
        for method in methods:
            assert inspect.signature(getattr(sync_cls, method)).parameters == (
                inspect.signature(getattr(async_cls, method)).parameters
            )


def test_mexc_advanced_sync_forwards_expected_parameters() -> None:
    trade = object.__new__(MexcTrade)
    trade._native_private = Mock(return_value={"success": True})
    trade.amend_contract_limit_order(123, "10", "2")
    trade._native_private.assert_called_with(
        "amend_contract_limit_order", [("orderId", "123"), ("price", "10"), ("vol", "2")]
    )
    trade.cancel_contract_tpsl_orders([{"stopPlanOrderId": 123}])
    trade._native_private.assert_called_with(
        "cancel_contract_tpsl_orders", [("orders", '[{"stopPlanOrderId":123}]')]
    )
    account = object.__new__(MexcAccount)
    account._native_private = Mock(return_value={"success": True})
    account.change_contract_multi_asset_mode(True)
    account._native_private.assert_called_with(
        "change_contract_multi_asset_mode", [("isMultiAssetMode", "true")]
    )
