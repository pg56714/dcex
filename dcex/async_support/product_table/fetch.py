"""Asynchronous Python compatibility functions for the Rust product table."""

import polars as pl

from ... import _native
from ...product_table.fetch import MarketInfo as MarketInfo


async def _fetch(exchange: str) -> pl.DataFrame:
    return pl.DataFrame(await _native.fetch_product_table_async(exchange))


async def aster() -> pl.DataFrame:
    """Fetch Aster product metadata."""
    return await _fetch("aster")


async def backpack() -> pl.DataFrame:
    """Fetch Backpack product metadata."""
    return await _fetch("backpack")


async def binance() -> pl.DataFrame:
    """Fetch Binance product metadata."""
    return await _fetch("binance")


async def bingx() -> pl.DataFrame:
    """Fetch BingX product metadata."""
    return await _fetch("bingx")


async def bitget() -> pl.DataFrame:
    """Fetch Bitget product metadata."""
    return await _fetch("bitget")


async def bitmart() -> pl.DataFrame:
    """Fetch BitMart product metadata."""
    return await _fetch("bitmart")


async def bitmex() -> pl.DataFrame:
    """Fetch BitMEX product metadata."""
    return await _fetch("bitmex")


async def bybit() -> pl.DataFrame:
    """Fetch Bybit product metadata."""
    return await _fetch("bybit")


async def gateio() -> pl.DataFrame:
    """Fetch Gate.io product metadata."""
    return await _fetch("gateio")


async def hyperliquid() -> pl.DataFrame:
    """Fetch Hyperliquid product metadata."""
    return await _fetch("hyperliquid")


async def kucoin() -> pl.DataFrame:
    """Fetch KuCoin product metadata."""
    return await _fetch("kucoin")


async def kraken() -> pl.DataFrame:
    """Fetch Kraken product metadata."""
    return await _fetch("kraken")


async def lighter() -> pl.DataFrame:
    """Fetch Lighter product metadata."""
    return await _fetch("lighter")


async def mexc() -> pl.DataFrame:
    """Fetch MEXC product metadata."""
    return await _fetch("mexc")


async def okx() -> pl.DataFrame:
    """Fetch OKX product metadata."""
    return await _fetch("okx")
