"""Common constants and enumerations used across the library."""

from enum import Enum


class Common(str, Enum):
    """Common exchange identifiers."""

    ASTER = "aster"
    BACKPACK = "backpack"
    BYBIT = "bybit"
    OKX = "okx"
    BITMART = "bitmart"
    GATEIO = "gateio"
    EXTENDED = "extended"
    BINANCE = "binance"
    HYPERLIQUID = "hyperliquid"
    BINGX = "bingx"
    BITGET = "bitget"
    KUCOIN = "kucoin"
    BITMEX = "bitmex"
    KRAKEN = "kraken"
    LIGHTER = "lighter"
    MEXC = "mexc"

    def __str__(self) -> str:
        return self.value
