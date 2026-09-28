"""Round-four reported holes are rejected by actual sync/async endpoints."""

import importlib
import inspect
from unittest.mock import AsyncMock

import pytest

CASES = [
    ("binance", "place_order", "icebergQty"),
    ("binance", "place_futures_algo_order", "activatePrice"),
    ("binance", "borrow_flexible_loan", "loanAmount"),
    ("okx", "amend_order", "newPx"),
    ("okx", "amend_algo_order", "newSz"),
    ("bybit", "place_order", "tpLimitPrice"),
    ("bybit", "set_trading_stop", "tpLimitPrice"),
    ("bitget", "place_futures_order", "presetStopLossPrice"),
    ("mexc", "place_contract_trailing_order", "activePrice"),
    ("bingx", "transfer_subaccount_assets", "transferAmount"),
    ("backpack", "place_order", "takeProfitTriggerPrice"),
    ("binance", "create_universal_transfer", "amount"),
    ("bybit", "create_internal_transfer", "amount"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("exchange,method,key", CASES)
@pytest.mark.parametrize("value", [1e-7, "1e-7", "-3", "abc", "+5", "-5%"])
async def test_reported_invalid_values_stop_before_adapter(exchange, method, key, value, asynchronous):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    # No client/network state: validation must run before the adapter body.
    with pytest.raises(ValueError, match="decimal"):
        result = getattr(cls, method)(object(), **{key: value})
        if inspect.isawaitable(result):
            await result


@pytest.mark.asyncio
@pytest.mark.parametrize("event", ["addOrder", "editOrder"])
@pytest.mark.parametrize("price", ["+5", "-5", "#5", "-5%", "+5.25%", "#5.5%"])
async def test_kraken_relative_price_reaches_native_unchanged(event, price):
    import json
    from dcex.ws.kraken import V1Client
    client = object.__new__(V1Client)
    client._native_client = AsyncMock()
    await client.send_message({"event": event, "price": price, "volume": "1"})
    assert json.loads(client._native_client.send_message.call_args.args[0])["price"] == price
