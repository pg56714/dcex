"""Regression coverage for the current BitMEX REST parameter surface."""

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
    "get_instrument_info": {
        "columns",
        "count",
        "start",
        "reverse",
        "startTime",
        "endTime",
    },
    "get_trades": {"pool"},
    "get_ticker": {"pool"},
    "get_kline": {"pool"},
    "place_order": {"pool", "strategy", "expiryTime", "maxSlippagePct"},
    "amend_order": {"expiryTime", "maxSlippagePct"},
    "get_order": {"pool", "targetAccountIds_array"},
    "get_executions": {"pool", "targetAccountIds_array"},
    "get_trade_history": {"pool", "targetAccountIds_array"},
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_bitmex_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "bitmex")
    async_client = _client_class("async", "bitmex")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


def test_bitmex_obsolete_liquidation_and_wallet_fields_are_not_exposed() -> None:
    client = _client_class("sync", "bitmex")
    liquidation_fields = set(inspect.signature(client.get_liquidations).parameters)
    wallet_fields = set(inspect.signature(client.get_wallet_summary).parameters)

    assert liquidation_fields.isdisjoint({"startTime", "endTime"})
    assert wallet_fields.isdisjoint({"target_account_id", "target_account_ids"})


def test_bitmex_current_official_defaults() -> None:
    client = _client_class("sync", "bitmex")
    assert inspect.signature(client.place_order).parameters["side"].default is None
    assert inspect.signature(client.place_order).parameters["ordType"].default is None
    assert inspect.signature(client.get_wallet_summary).parameters["currency"].default == "XBt"
    assert inspect.signature(client.get_margin).parameters["currency"].default == "XBt"


def test_sync_bitmex_serializes_filters_and_query_arrays() -> None:
    client = _client_class("sync", "bitmex")(**_client_kwargs("bitmex"))
    calls = _wire_sync(client)

    client.get_trades(
        product_symbol="XBT-USD-SWAP",
        filter={"side": "Buy"},
        columns=["symbol", "price"],
        pool="Aggregated",
    )
    client.get_positions(target_account_ids=[123, 456])

    assert dict(calls[0]["query"]) == {
        "product_symbol": "XBTUSDT",
        "filter": '{"side":"Buy"}',
        "columns": '["symbol","price"]',
        "pool": "Aggregated",
    }
    assert calls[1]["query"] == [
        ("targetAccountIds[]", "123"),
        ("targetAccountIds[]", "456"),
    ]


@pytest.mark.asyncio
async def test_async_bitmex_forwards_v2_order_and_amend_fields() -> None:
    client = _client_class("async", "bitmex")(**_client_kwargs("bitmex"))
    calls = _wire_async(client)

    await client.place_order(
        "XBT-USD-SWAP",
        orderQty=1,
        price=100_000,
        pool="Primary",
        strategy="OneWay",
    )
    await client.amend_order(
        orderID="00000000-0000-0000-0000-000000000001",
        expiryTime="2026-11-05T00:00:00.555Z",
        maxSlippagePct=1.5,
    )

    assert dict(calls[0]["query"])["pool"] == "Primary"
    assert dict(calls[0]["query"])["strategy"] == "OneWay"
    assert dict(calls[1]["query"])["expiryTime"] == "2026-11-05T00:00:00.555Z"
    assert dict(calls[1]["query"])["maxSlippagePct"] == "1.5"


def test_bitmex_cancel_requires_an_identifier_before_transport() -> None:
    client = _client_class("sync", "bitmex")(**_client_kwargs("bitmex"))
    _wire_sync(client)

    with pytest.raises(ValueError, match="Either orderID or clOrdID"):
        client.cancel_order()


def test_bitmex_generic_order_does_not_override_official_type_inference() -> None:
    client = _client_class("sync", "bitmex")(**_client_kwargs("bitmex"))
    calls = _wire_sync(client)

    client.place_order(
        "XBT-USD-SWAP",
        orderQty=1,
        price=99_000,
        stopPx=100_000,
    )

    assert "ordType" not in dict(calls[0]["query"])
