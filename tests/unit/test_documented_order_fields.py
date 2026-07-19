"""Regression coverage for exchange order fields documented by official APIs."""
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

ORDER_FIELD_CASES: tuple[tuple[str, str, dict[str, Any], set[str]], ...] = (
    (
        "bitget",
        "place_uta_order",
        {
            "category": "USDT-FUTURES",
            "product_symbol": "BTC-USDT-SWAP",
            "side": "buy",
            "orderType": "limit",
            "qty": "1",
            "takeProfit": "110",
            "stopLoss": "90",
            "tpLimitPrice": "109",
            "slLimitPrice": "89",
        },
        {"takeProfit", "stopLoss", "tpLimitPrice", "slLimitPrice"},
    ),
    (
        "bitget",
        "place_futures_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "side": "buy",
            "orderType": "limit",
            "size": "1",
            "presetStopSurplusPrice": "110",
            "presetStopLossExecutePrice": "89",
            "stpMode": "cancel_taker",
        },
        {"presetStopSurplusPrice", "presetStopLossExecutePrice", "stpMode"},
    ),
    (
        "kraken",
        "place_spot_order",
        {
            "product_symbol": "BTC-USD-SPOT",
            "side": "buy",
            "ordertype": "limit",
            "volume": "1",
            "close_ordertype": "stop-loss",
            "close_price": "90",
            "deadline": "2026-07-19T12:00:00Z",
        },
        {"close[ordertype]", "close[price]", "deadline"},
    ),
    (
        "kraken",
        "place_futures_order",
        {
            "product_symbol": "BTC-USD-SWAP",
            "side": "buy",
            "orderType": "trailing_stop",
            "size": "1",
            "trailingStopMaxDeviation": "1",
            "trailingStopDeviationUnit": "percent",
        },
        {"trailingStopMaxDeviation", "trailingStopDeviationUnit"},
    ),
    (
        "mexc",
        "place_contract_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "side": 1,
            "type_": 1,
            "openType": 2,
            "vol": "1",
            "bboTypeNum": 1,
            "stpMode": 3,
            "marketCeiling": True,
        },
        {"bboTypeNum", "stpMode", "marketCeiling"},
    ),
    (
        "bitmex",
        "place_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "side": "buy",
            "expiryTime": "2026-11-05T00:00:00.555Z",
            "maxSlippagePct": 1.5,
        },
        {"expiryTime", "maxSlippagePct"},
    ),
    (
        "bingx",
        "place_spot_order",
        {
            "product_symbol": "BTC-USDT-SPOT",
            "side": "buy",
            "type_": "TRIGGER_LIMIT",
            "stopPrice": "90",
            "newClientOrderId": "doc-id",
        },
        {"stopPrice", "newClientOrderId"},
    ),
    (
        "backpack",
        "place_order",
        {
            "product_symbol": "BTC-USDC-SWAP",
            "side": "Bid",
            "orderType": "Limit",
            "triggerPrice": "90",
            "stopLossTriggerPrice": "85",
            "slippageTolerance": "0.5",
        },
        {"triggerPrice", "stopLossTriggerPrice", "slippageTolerance"},
    ),
    (
        "aster",
        "place_futures_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "side": "buy",
            "type_": "LIMIT",
            "quantity": "1",
            "pegPriceType": "QUEUE_1",
            "pegOffset": "-0.5",
        },
        {"pegPriceType", "pegOffset"},
    ),
)


@pytest.mark.parametrize(("exchange", "method_name", "kwargs", "expected_keys"), ORDER_FIELD_CASES)
def test_sync_documented_order_fields_are_forwarded(
    exchange: str,
    method_name: str,
    kwargs: dict[str, Any],
    expected_keys: set[str],
) -> None:
    client = _client_class("sync", exchange)(**_client_kwargs(exchange))
    calls = _wire_sync(client)

    assert getattr(client, method_name)(**kwargs) == {"ok": True}
    assert expected_keys <= set(dict(calls[0]["query"]))


@pytest.mark.asyncio
@pytest.mark.parametrize(("exchange", "method_name", "kwargs", "expected_keys"), ORDER_FIELD_CASES)
async def test_async_documented_order_fields_are_forwarded(
    exchange: str,
    method_name: str,
    kwargs: dict[str, Any],
    expected_keys: set[str],
) -> None:
    client = _client_class("async", exchange)(**_client_kwargs(exchange))
    calls = _wire_async(client)

    assert await getattr(client, method_name)(**kwargs) == {"ok": True}
    assert expected_keys <= set(dict(calls[0]["query"]))
