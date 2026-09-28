"""Offline coverage for bitget reality wrappers."""
# ruff: noqa: D103

from unittest.mock import AsyncMock

import pytest

from dcex.async_support.bitget._account_http import AccountHTTP as AsyncBitgetAccount


@pytest.mark.asyncio
async def test_bitget_reality_async_forwards_signed_read() -> None:
    account = object.__new__(AsyncBitgetAccount)
    account._native_private = AsyncMock(return_value={"code": "00000"})
    await account.get_reality_fills("RAAPLUSDT", limit=20)
    account._native_private.assert_called_with(
        "get_reality_fills", [("product_symbol", "RAAPLUSDT"), ("limit", "20")]
    )
