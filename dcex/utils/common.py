"""Common constants and enumerations used across the library."""

from enum import Enum


class Common(str, Enum):
    """Common exchange identifiers."""

    BYBIT = "bybit"
    OKX = "okx"
    BITMART = "bitmart"
    GATEIO = "gateio"
    BINANCE = "binance"
    HYPERLIQUID = "hyperliquid"
    BINGX = "bingx"
    KUCOIN = "kucoin"
    BITMEX = "bitmex"
    ZOOMEX = "zoomex"

    def __str__(self) -> str:
        return self.value
