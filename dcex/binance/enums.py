"""Binance product type enumerations."""

from enum import Enum


class BinanceProductType(str, Enum):
    """Enumeration for Binance product types."""

    SPOT = "spot"
    SWAP = "swap"

    def __str__(self) -> str:
        return self.value
