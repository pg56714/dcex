"""Synchronous Python compatibility functions for the Rust product table."""

from dataclasses import asdict, dataclass

from .. import _native

ProductTable = _native.ProductTable


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


def _fetch(exchange: str) -> ProductTable:
    return _native.fetch_product_table(exchange)


def aster() -> ProductTable:
    """Fetch Aster product metadata."""
    return _fetch("aster")


def backpack() -> ProductTable:
    """Fetch Backpack product metadata."""
    return _fetch("backpack")


def binance() -> ProductTable:
    """Fetch Binance product metadata."""
    return _fetch("binance")


def bingx() -> ProductTable:
    """Fetch BingX product metadata."""
    return _fetch("bingx")


def bitget() -> ProductTable:
    """Fetch Bitget product metadata."""
    return _fetch("bitget")


def bitmex() -> ProductTable:
    """Fetch BitMEX product metadata."""
    return _fetch("bitmex")


def bybit() -> ProductTable:
    """Fetch Bybit product metadata."""
    return _fetch("bybit")


def extended() -> ProductTable:
    """Fetch Extended product metadata."""
    return _fetch("extended")


def hyperliquid() -> ProductTable:
    """Fetch Hyperliquid product metadata."""
    return _fetch("hyperliquid")


def kucoin() -> ProductTable:
    """Fetch KuCoin product metadata."""
    return _fetch("kucoin")


def kraken() -> ProductTable:
    """Fetch Kraken product metadata."""
    return _fetch("kraken")


def lighter() -> ProductTable:
    """Fetch Lighter product metadata."""
    return _fetch("lighter")


def mexc() -> ProductTable:
    """Fetch MEXC product metadata."""
    return _fetch("mexc")


def okx() -> ProductTable:
    """Fetch OKX product metadata."""
    return _fetch("okx")
