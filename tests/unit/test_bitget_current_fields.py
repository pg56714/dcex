"""Regression coverage for current Bitget REST parameter surfaces."""
# ruff: noqa: D103

from __future__ import annotations

import inspect

import pytest

from tests.unit.endpoint_wrapper_helpers import _client_class

CURRENT_FIELDS = {
    "place_spot_order": {
        "triggerPrice",
        "requestTime",
        "receiveWindow",
        "presetTakeProfitPrice",
        "executeTakeProfitPrice",
        "presetStopLossPrice",
        "executeStopLossPrice",
    },
    "get_spot_order": {"requestTime", "receiveWindow"},
    "get_spot_open_orders": {"orderId", "tpslType", "requestTime", "receiveWindow"},
    "get_spot_history_orders": {"orderId", "tpslType", "requestTime", "receiveWindow"},
    "get_futures_kline": {"kLineType"},
    "get_uta_liquidations": {"category", "cursor"},
    "get_futures_account_bills": {"coin", "businessType", "onlyFunding", "idLessThan"},
    "set_futures_leverage": {"leverage", "longLeverage", "shortLeverage"},
    "get_uta_all_fee_rates": {"category", "product_symbol", "symbol"},
    "get_futures_open_orders": {"status", "startTime", "endTime"},
    "get_futures_history_orders": {"orderId", "clientOid", "orderSource"},
    "get_uta_history_strategy_orders": {"cursor"},
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
