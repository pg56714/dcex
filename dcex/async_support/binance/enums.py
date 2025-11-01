"""Binance exchange type enumerations."""

from enum import Enum


class BinanceProductType(str, Enum):
    """Binance exchange types for spot and futures trading."""

    SPOT = "spot"
    SWAP = "swap"

    def __str__(self) -> str:
        return self.value
