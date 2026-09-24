"""Offline Python-to-Rust checks for Binance COIN-M and Convert wrappers."""

import pytest

from dcex.async_support.binance.client import Client as AsyncClient
from dcex.binance.client import Client


def test_sync_new_wrappers_reach_rust_validation() -> None:
    """Synchronous wrappers reach Rust validation without network requests."""
    client = Client(preload_product_table=False)
    try:
        with pytest.raises(ValueError, match="fromAsset or toAsset"):
            client.get_convert_pairs()
        with pytest.raises(ValueError, match="native Binance symbol"):
            client.get_coin_futures_orderbook("BTC-USD-SWAP")
        with pytest.raises(ValueError, match="exactly one"):
            client.get_convert_quote("BTC", "USDT", fromAmount="1", toAmount="2")
    finally:
        client.close()


@pytest.mark.asyncio
async def test_async_new_wrappers_reach_rust_validation() -> None:
    """Asynchronous wrappers reach Rust validation without network requests."""
    client = AsyncClient(preload_product_table=False)
    await client.async_init()
    try:
        with pytest.raises(ValueError, match="fromAsset or toAsset"):
            await client.get_convert_pairs()
        with pytest.raises(ValueError, match="native Binance symbol"):
            await client.get_coin_futures_orderbook("BTC-USD-SWAP")
        with pytest.raises(ValueError, match="exactly one"):
            await client.get_convert_quote("BTC", "USDT", fromAmount="1", toAmount="2")
    finally:
        await client.close()
