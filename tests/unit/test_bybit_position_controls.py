"""Offline sync/async wrapper tests for Bybit position controls."""

import asyncio
from unittest.mock import AsyncMock, Mock

from dcex.async_support.bybit._position_http import PositionHTTP as AsyncPositionHTTP
from dcex.bybit._position_http import PositionHTTP


def test_sync_position_controls_forward_to_rust() -> None:
    """Synchronous methods preserve the Bybit field names expected by Rust."""
    client = object.__new__(PositionHTTP)
    client._native_private = Mock(return_value={"ok": True})
    client.set_trading_stop("BTC-USDT-SWAP", "Full", 0, take_profit="120000", stop_loss="90000")
    client.add_position_margin("BTC-USD-SWAP", "-10.25", 2)
    client.set_auto_add_margin("BTC-USDT-SWAP", True)
    calls = client._native_private.call_args_list
    assert calls[0].args == (
        "set_trading_stop",
        [
            ("product_symbol", "BTC-USDT-SWAP"),
            ("tpslMode", "Full"),
            ("positionIdx", "0"),
            ("takeProfit", "120000"),
            ("stopLoss", "90000"),
        ],
    )
    assert calls[1].args == (
        "add_position_margin",
        [("product_symbol", "BTC-USD-SWAP"), ("margin", "-10.25"), ("positionIdx", "2")],
    )
    assert calls[2].args == (
        "set_auto_add_margin",
        [("product_symbol", "BTC-USDT-SWAP"), ("autoAddMargin", "1")],
    )


def test_async_position_controls_forward_to_rust() -> None:
    """Asynchronous methods forward the same position-control fields."""
    async def check() -> None:
        client = object.__new__(AsyncPositionHTTP)
        client._native_private = AsyncMock(return_value={"ok": True})
        await client.set_trading_stop("BTC-USDT-SWAP", "Full", 0, stop_loss="90000")
        await client.add_position_margin("BTC-USDT-SWAP", "10")
        await client.set_auto_add_margin("BTC-USDT-SWAP", False, 1)
        calls = client._native_private.call_args_list
        assert [call.args[0] for call in calls] == [
            "set_trading_stop",
            "add_position_margin",
            "set_auto_add_margin",
        ]
        assert calls[2].args[1] == [
            ("product_symbol", "BTC-USDT-SWAP"),
            ("autoAddMargin", "0"),
            ("positionIdx", "1"),
        ]

    asyncio.run(check())
