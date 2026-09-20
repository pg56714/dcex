"""Offline coverage for stock-specific Python method forwarding."""

# ruff: noqa: D103

from unittest.mock import AsyncMock, Mock

import pytest

from dcex.async_support.backpack._trade_http import TradeHTTP as AsyncBackpackTradeHTTP
from dcex.async_support.binance._trade_http import TradeHTTP as AsyncBinanceTradeHTTP
from dcex.backpack._trade_http import TradeHTTP as BackpackTradeHTTP
from dcex.binance._trade_http import TradeHTTP as BinanceTradeHTTP


def test_binance_equity_named_sync_methods() -> None:
    client = object.__new__(BinanceTradeHTTP)
    client._native_private = Mock(return_value={"ok": True})

    assert client.cancel_all_equity_orders() == {"ok": True}
    client._native_private.assert_called_with("cancel_all_equity_orders", [])
    client.get_equity_trade_history(10, 20, product_symbol="AAPL-USDT-SPOT", size=5)
    client._native_private.assert_called_with(
        "get_equity_trade_history",
        [
            ("startTime", "10"),
            ("endTime", "20"),
            ("product_symbol", "AAPL-USDT-SPOT"),
            ("size", "5"),
        ],
    )
    client.mint_equity_token("USDT", "10", "mint-1")
    client._native_private.assert_called_with(
        "mint_equity_token",
        [
            ("underlyingAsset", "USDT"),
            ("underlyingAssetAmount", "10"),
            ("clientOrderId", "mint-1"),
        ],
    )
    client.redeem_equity_token("AAPL", "0.5")
    client._native_private.assert_called_with(
        "redeem_equity_token",
        [("tokenizedAsset", "AAPL"), ("tokenizedAssetAmount", "0.5")],
    )
    client.get_equity_convert_status("request-1", "MINT")
    client._native_private.assert_called_with(
        "get_equity_convert_status",
        [("issuerRequestId", "request-1"), ("convertType", "MINT")],
    )
    client.get_equity_convert_history(start_time=10, end_time=20, size=5)
    client._native_private.assert_called_with(
        "get_equity_convert_history",
        [("startTime", "10"), ("endTime", "20"), ("size", "5")],
    )
    client.sign_equity_disclaimer()
    client._native_private.assert_called_with("sign_equity_disclaimer", [])
    client.create_or_renew_equity_listen_key()
    client._native_private.assert_called_with("create_or_renew_equity_listen_key", [])


@pytest.mark.asyncio
async def test_binance_equity_named_async_methods() -> None:
    client = object.__new__(AsyncBinanceTradeHTTP)
    client._native_private = AsyncMock(return_value={"ok": True})

    assert await client.cancel_all_equity_orders() == {"ok": True}
    await client.get_equity_trade_history(10, 20)
    client._native_private.assert_called_with(
        "get_equity_trade_history", [("startTime", "10"), ("endTime", "20")]
    )
    await client.mint_equity_token("USDT", "10")
    client._native_private.assert_called_with(
        "mint_equity_token",
        [("underlyingAsset", "USDT"), ("underlyingAssetAmount", "10")],
    )
    await client.redeem_equity_token("AAPL", "1")
    await client.get_equity_convert_status("request-1", "REDEEM")
    await client.get_equity_convert_history()
    await client.sign_equity_disclaimer()
    await client.create_or_renew_equity_listen_key()
    assert client._native_private.await_count == 8


def test_backpack_rfq_named_sync_methods() -> None:
    client = object.__new__(BackpackTradeHTTP)
    client._native_private = Mock(return_value={"ok": True})

    assert client.get_rfqs("AAPL_USDC_RFQ") == {"ok": True}
    client.submit_rfq("AAPL_USDC_RFQ", "Bid", quantity="1")
    client._native_private.assert_called_with(
        "submit_rfq",
        [
            ("product_symbol", "AAPL_USDC_RFQ"),
            ("side", "Bid"),
            ("quantity", "1"),
            ("executionMode", "AwaitAccept"),
        ],
    )
    client.accept_rfq_quote("quote-1", rfq_id="rfq-1")
    client.refresh_rfq("rfq-1")
    client.cancel_rfq(rfq_id="rfq-1")
    client.get_rfq_history()
    client.get_quote_history()
    client.get_rfq_fill_history()
    client.get_quote_fill_history()
    assert client._native_private.call_count == 9
    with pytest.raises(ValueError, match="exactly one"):
        client.accept_rfq_quote("quote-1")
    with pytest.raises(ValueError, match="exactly one"):
        client.cancel_rfq(rfq_id="rfq-1", client_id=1)


@pytest.mark.asyncio
async def test_backpack_rfq_named_async_methods() -> None:
    client = object.__new__(AsyncBackpackTradeHTTP)
    client._native_private = AsyncMock(return_value={"ok": True})

    await client.get_rfqs()
    await client.submit_rfq("AAPL_USDC_RFQ", "Ask", quantity="2")
    await client.accept_rfq_quote("quote-1", client_id=1)
    await client.refresh_rfq("rfq-1")
    await client.cancel_rfq(client_id=1)
    await client.get_rfq_history()
    await client.get_quote_history()
    await client.get_rfq_fill_history()
    await client.get_quote_fill_history()
    assert client._native_private.await_count == 9
    with pytest.raises(ValueError, match="exactly one"):
        await client.cancel_rfq()
