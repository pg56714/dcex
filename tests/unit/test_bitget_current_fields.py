"""Regression coverage for current Bitget REST parameter surfaces."""
# ruff: noqa: D103

from __future__ import annotations

import inspect

import pytest

from tests.unit.endpoint_wrapper_helpers import _client_class

CURRENT_FIELDS = {
    "place_spot_order": {
        "execute_stop_loss_price",
        "execute_take_profit_price",
        "preset_stop_loss_price",
        "preset_take_profit_price",
        "receive_window",
        "request_time",
        "trigger_price",
    },
    "get_spot_order": {"receive_window", "request_time"},
    "get_spot_open_orders": {"receive_window", "request_time", "tpsl_type", "order_id"},
    "get_spot_history_orders": {"receive_window", "request_time", "tpsl_type", "order_id"},
    "get_futures_kline": {"k_line_type"},
    "get_uta_liquidations": {"category", "cursor"},
    "get_uta_instruments": {"category", "symbol", "product_symbol"},
    "get_uta_kline": {"category", "type_", "interval", "product_symbol"},
    "get_reality_stock_info": {"symbol", "product_symbol"},
    "place_reality_order": {"category", "qty", "product_symbol", "order_type"},
    "cancel_reality_order": {"category", "product_symbol", "order_id", "client_oid"},
    "get_futures_account_bills": {"coin", "only_funding", "id_less_than", "business_type"},
    "set_futures_leverage": {"long_leverage", "leverage", "short_leverage"},
    "get_uta_all_fee_rates": {"category", "symbol", "product_symbol"},
    "get_futures_open_orders": {"end_time", "start_time", "status"},
    "get_futures_history_orders": {"order_source", "order_id", "client_oid"},
    "get_uta_history_strategy_orders": {"cursor"},
    "get_crypto_loan_coins": {"coin"},
    "get_crypto_loan_interest": {"loan_coin", "pledge_coin", "pledge_amount", "daily"},
    "borrow_crypto_loan": {"pledge_coin", "loan_coin", "loan_amount", "pledge_amount", "daily"},
    "get_crypto_loan_borrow_history": {"start_time", "end_time", "status"},
    "repay_crypto_loan": {"order_id", "amount", "repay_unlock", "repay_all"},
    "get_crypto_loan_pledge_history": {"start_time", "end_time", "revise_side"},
    "get_crypto_loan_liquidations": {"start_time", "end_time", "status"},
    "repay_uta_liability": {"repayable_coin_list", "payment_coin_list"},
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_bitget_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "bitget")
    async_client = _client_class("async", "bitget")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


@pytest.mark.parametrize(
    ("method_name", "obsolete"),
    [
        ("get_spot_history_kline", {"startTime"}),
        ("get_uta_liquidations", {"startTime", "endTime"}),
        ("get_futures_account_bills", {"symbol", "marginCoin", "lastEndId"}),
        ("get_uta_loan_data", {"coin"}),
        ("get_uta_collateral_type", {"coin"}),
        ("get_uta_unfilled_strategy_orders", {"product_symbol", "idLessThan", "limit"}),
        ("get_uta_history_strategy_orders", {"product_symbol", "idLessThan"}),
    ],
)
def test_bitget_obsolete_fields_are_not_exposed(method_name: str, obsolete: set[str]) -> None:
    client = _client_class("sync", "bitget")
    fields = set(inspect.signature(getattr(client, method_name)).parameters)
    assert fields.isdisjoint(obsolete)
