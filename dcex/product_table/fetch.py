"""Synchronous Python compatibility functions for the Rust product table."""

from dataclasses import asdict, dataclass

import polars as pl

from .. import _native


@dataclass
class MarketInfo:
    """Standardized exchange market metadata."""

    exchange: str
    exchange_symbol: str
    product_symbol: str
    product_type: str
    exchange_type: str
    price_precision: str
    size_precision: str
    min_size: str
    base_currency: str = ""
    quote_currency: str = ""
    min_notional: str = "0"
    size_per_contract: str = "1"

    def to_dict(self) -> dict[str, str]:
        """Return the market metadata as a dictionary."""
        return asdict(self)


def _fetch(exchange: str) -> pl.DataFrame:
    return pl.DataFrame(_native.fetch_product_table(exchange))


def aster() -> pl.DataFrame:
    """Fetch Aster product metadata."""
    return _fetch("aster")


def backpack() -> pl.DataFrame:
    """Fetch Backpack product metadata."""
    return _fetch("backpack")


def binance() -> pl.DataFrame:
    """Fetch Binance product metadata."""
    return _fetch("binance")


def bingx() -> pl.DataFrame:
    """Fetch BingX product metadata."""
    return _fetch("bingx")


def bitget() -> pl.DataFrame:
    """Fetch Bitget product metadata."""
    return _fetch("bitget")


def bitmart() -> pl.DataFrame:
    """Fetch BitMart product metadata."""
    return _fetch("bitmart")


def bitmex() -> pl.DataFrame:
    """Fetch BitMEX product metadata."""
    return _fetch("bitmex")


def bybit() -> pl.DataFrame:
    """Fetch Bybit product metadata."""
    return _fetch("bybit")


def gateio() -> pl.DataFrame:
    """Fetch Gate.io product metadata."""
    return _fetch("gateio")


def hyperliquid() -> pl.DataFrame:
    """Fetch Hyperliquid product metadata."""
    return _fetch("hyperliquid")


def kucoin() -> pl.DataFrame:
    """Fetch KuCoin product metadata."""
    return _fetch("kucoin")


def kraken() -> pl.DataFrame:
    """Fetch Kraken product metadata."""
    return _fetch("kraken")


def lighter() -> pl.DataFrame:
    """Fetch Lighter product metadata."""
    return _fetch("lighter")


def mexc() -> pl.DataFrame:
    """Fetch MEXC product metadata."""
    return _fetch("mexc")


def okx() -> pl.DataFrame:
    """Fetch OKX product metadata."""
    return _fetch("okx")
