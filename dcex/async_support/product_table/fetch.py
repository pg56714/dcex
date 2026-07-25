"""Asynchronous Python compatibility functions for the Rust product table."""

from ... import _native
from ...product_table.fetch import MarketInfo as MarketInfo
from ...product_table.fetch import ProductTable as ProductTable


async def _fetch(exchange: str) -> ProductTable:
    return await _native.fetch_product_table_async(exchange)


async def aster() -> ProductTable:
    """Fetch Aster product metadata."""
    return await _fetch("aster")


async def backpack() -> ProductTable:
    """Fetch Backpack product metadata."""
    return await _fetch("backpack")


async def binance() -> ProductTable:
    """Fetch Binance product metadata."""
    return await _fetch("binance")


async def bingx() -> ProductTable:
    """Fetch BingX product metadata."""
    return await _fetch("bingx")


async def bitget() -> ProductTable:
    """Fetch Bitget product metadata."""
    return await _fetch("bitget")


async def bybit() -> ProductTable:
    """Fetch Bybit product metadata."""
    return await _fetch("bybit")


async def extended() -> ProductTable:
    """Fetch Extended product metadata."""
    return await _fetch("extended")


async def hyperliquid() -> ProductTable:
    """Fetch Hyperliquid product metadata."""
    return await _fetch("hyperliquid")


async def kucoin() -> ProductTable:
    """Fetch KuCoin product metadata."""
    return await _fetch("kucoin")


async def kraken() -> ProductTable:
    """Fetch Kraken product metadata."""
    return await _fetch("kraken")


async def lighter() -> ProductTable:
    """Fetch Lighter product metadata."""
    return await _fetch("lighter")


async def mexc() -> ProductTable:
    """Fetch MEXC product metadata."""
    return await _fetch("mexc")


async def okx() -> ProductTable:
    """Fetch OKX product metadata."""
    return await _fetch("okx")
