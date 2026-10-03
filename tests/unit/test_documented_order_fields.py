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
        "binance",
        "place_order",
        {
            "product_symbol": "BTC-USDT-SPOT",
            "side": "buy",
            "type_": "LIMIT",
            "quantity": "1",
            "strategyId": 42,
            "strategyType": 1_000_000,
            "trailingDelta": 100,
            "icebergQty": "0.1",
            "pegPriceType": "PRIMARY_PEG",
            "pegOffsetValue": 2,
            "pegOffsetType": "PRICE_LEVEL",
        },
        {
            "strategyId",
            "strategyType",
            "trailingDelta",
            "icebergQty",
            "pegPriceType",
            "pegOffsetValue",
            "pegOffsetType",
        },
    ),
    (
        "binance",
        "test_order",
        {
            "product_symbol": "BTC-USDT-SPOT",
            "side": "buy",
            "type_": "MARKET",
            "quantity": "1",
            "computeCommissionRates": True,
        },
        {"computeCommissionRates"},
    ),
    (
        "okx",
        "place_order",
        {
            "product_symbol": "BTC-USDT-SPOT",
            "tdMode": "cash",
            "side": "buy",
            "ordType": "market",
            "sz": "1",
            "reduceOnly": True,
            "banAmend": False,
            "outcome": "yes",
            "pxAmendType": "1",
            "tradeQuoteCcy": "USDT",
            "slippagePct": "0.0123",
            "tgtCcy": "base_ccy",
            "isElpTakerAccess": True,
            "rpiTakerAccess": True,
            "rpiPxRound": True,
            "attachAlgoOrds": [{"tpTriggerPx": "110", "tpOrdPx": "109"}],
        },
        {
            "outcome",
            "pxAmendType",
            "tradeQuoteCcy",
            "slippagePct",
            "isElpTakerAccess",
            "rpiTakerAccess",
            "rpiPxRound",
            "attachAlgoOrds",
        },
    ),
    (
        "bitget",
        "place_uta_order",
        {
            "category": "USDT-FUTURES",
            "product_symbol": "BTC-USDT-SWAP",
            "side": "buy",
            "order_type": "limit",
            "qty": "1",
            "take_profit": "110",
            "stop_loss": "90",
            "tp_limit_price": "109",
            "sl_limit_price": "89",
        },
        {"takeProfit", "stopLoss", "tpLimitPrice", "slLimitPrice"},
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
        "bingx",
        "place_spot_order",
        {
            "product_symbol": "BTC-USDT-SPOT",
            "side": "buy",
            "type_": "TRIGGER_LIMIT",
            "stop_price": "90",
            "new_client_order_id": "doc-id",
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
