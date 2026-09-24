"""Offline coverage for Binance Options Python method forwarding."""

# ruff: noqa: D103

from unittest.mock import AsyncMock, Mock

import pytest

from dcex.async_support.binance._account_http import AccountHTTP as AsyncAccountHTTP
from dcex.async_support.binance._market_http import MarketHTTP as AsyncMarketHTTP
from dcex.async_support.binance._trade_http import TradeHTTP as AsyncTradeHTTP
from dcex.binance._account_http import AccountHTTP
from dcex.binance._market_http import MarketHTTP
from dcex.binance._trade_http import TradeHTTP


def test_sync_options_named_methods_forward_native_parameters() -> None:
    market = object.__new__(MarketHTTP)
    market._native_public = Mock(return_value={"ok": True})
    market.get_options_orderbook("BTC-260925-100000-C", limit=10)
    market._native_public.assert_called_with(
        "get_options_orderbook",
        [("product_symbol", "BTC-260925-100000-C"), ("limit", "10")],
    )

    account = object.__new__(AccountHTTP)
    account._native_private = Mock(return_value={"ok": True})
    account.get_options_account_bill("USDT", limit=20)
    account._native_private.assert_called_with(
        "get_options_account_bill", [("currency", "USDT"), ("limit", "20")]
    )

    trade = object.__new__(TradeHTTP)
    trade._native_private = Mock(return_value={"ok": True})
    trade.place_options_order(
        "BTC-260925-100000-C",
        "buy",
        "0.01",
        "1",
        postOnly=True,
    )
    trade._native_private.assert_called_with(
        "place_options_order",
        [
            ("product_symbol", "BTC-260925-100000-C"),
            ("side", "BUY"),
            ("type", "LIMIT"),
            ("quantity", "0.01"),
            ("price", "1"),
            ("timeInForce", "GTC"),
            ("postOnly", "true"),
        ],
    )
    trade.place_options_batch_orders(
        [{"symbol": "BTC-260925-100000-C", "side": "BUY", "quantity": "0.01"}]
    )
    assert trade._native_private.call_args.args[1][0][1].startswith('[{"symbol"')


@pytest.mark.asyncio
async def test_async_options_named_methods_forward_native_parameters() -> None:
    market = object.__new__(AsyncMarketHTTP)
    market._native_public = AsyncMock(return_value={"ok": True})
    await market.get_options_index_price("BTCUSDT")
    market._native_public.assert_awaited_with(
        "get_options_index_price", [("underlying", "BTCUSDT")]
    )

    account = object.__new__(AsyncAccountHTTP)
    account._native_private = AsyncMock(return_value={"ok": True})
    await account.create_options_listen_key()
    account._native_private.assert_awaited_with("create_options_listen_key", [])

    trade = object.__new__(AsyncTradeHTTP)
    trade._native_private = AsyncMock(return_value={"ok": True})
    await trade.cancel_options_order("BTC-260925-100000-C", clientOrderId="client-1")
    trade._native_private.assert_awaited_with(
        "cancel_options_order",
        [
            ("product_symbol", "BTC-260925-100000-C"),
            ("clientOrderId", "client-1"),
        ],
    )
