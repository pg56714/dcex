"""Regression coverage for current MEXC REST parameter surfaces."""

# ruff: noqa: D103

from __future__ import annotations

import inspect

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)

CURRENT_FIELDS = {
    "get_spot_exchange_info": {"product_symbol", "symbols"},
    "get_spot_agg_trades": {"product_symbol", "startTime", "endTime", "limit"},
    "test_spot_order": {"stpMode", "recvWindow"},
    "place_spot_order": {"stpMode", "recvWindow"},
    "place_spot_batch_orders": {"batchOrders", "recvWindow"},
    "cancel_spot_order": {"orderId", "origClientOrderId", "newClientOrderId"},
    "get_spot_order": {"product_symbol", "orderId", "origClientOrderId"},
    "get_contract_history_positions": {
        "product_symbol",
        "type_",
        "start_time",
        "end_time",
        "position_type",
        "page_num",
        "page_size",
    },
    "get_contract_funding_records": {
        "position_id",
        "position_type",
        "start_time",
        "end_time",
    },
    "change_contract_leverage": {
        "leverageMode",
        "marginSelected",
        "leverageSelected",
    },
    "place_contract_plan_order": {
        "vol",
        "leverage",
        "side",
        "openType",
        "triggerPrice",
        "triggerType",
        "executeCycle",
        "orderType",
        "trend",
    },
    "get_contract_stop_orders": {"is_finished", "state", "type_", "start_time", "end_time"},
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_mexc_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "mexc")
    async_client = _client_class("async", "mexc")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


@pytest.mark.parametrize(
    ("method_name", "obsolete"),
    [
        ("get_spot_exchange_info", {"status", "tradeSideType"}),
        ("get_spot_agg_trades", {"fromId"}),
        ("place_spot_order", {"timeInForce"}),
        ("get_spot_all_orders", {"orderId"}),
        ("get_contract_open_orders", {"product_symbol"}),
        ("get_contract_stop_orders", {"states"}),
    ],
)
def test_mexc_obsolete_fields_are_not_exposed(method_name: str, obsolete: set[str]) -> None:
    client = _client_class("sync", "mexc")
    fields = set(inspect.signature(getattr(client, method_name)).parameters)
    assert fields.isdisjoint(obsolete)


def test_mexc_current_kline_and_pagination_defaults() -> None:
    sync_client = _client_class("sync", "mexc")
    async_client = _client_class("async", "mexc")

    for client in (sync_client, async_client):
        assert inspect.signature(client.get_spot_klines).parameters["interval"].default == "1m"
        assert (
            inspect.signature(client.get_contract_fair_price_kline)
            .parameters["interval"]
            .default
            == "Min1"
        )
        history = inspect.signature(client.get_contract_history_orders).parameters
        assert history["page_num"].default == 1
        assert history["page_size"].default == 20


def test_sync_mexc_forwards_current_spot_order_fields() -> None:
    client = _client_class("sync", "mexc")(**_client_kwargs("mexc"))
    calls = _wire_sync(client)

    client.place_spot_limit_buy_order(
        "BTC-USDT-SPOT",
        "0.001",
        "100000",
        stpMode="CANCEL_MAKER",
        recvWindow=5_000,
    )

    assert dict(calls[0]["query"]) == {
        "product_symbol": "BTC-USDT-SPOT",
        "quantity": "0.001",
        "price": "100000",
        "stpMode": "CANCEL_MAKER",
        "recvWindow": "5000",
    }


@pytest.mark.asyncio
async def test_async_mexc_serializes_plan_order_cancellation_array() -> None:
    client = _client_class("async", "mexc")(**_client_kwargs("mexc"))
    calls = _wire_async(client)

    await client.cancel_contract_plan_orders(
        [{"symbol": "BTC_USDT", "orderId": "123"}]
    )

    assert dict(calls[0]["query"])["orders"] == '[{"symbol":"BTC_USDT","orderId":"123"}]'
