"""Ascendex spot market API endpoints."""

from enum import Enum


class SpotMarket(str, Enum):
    """Ascendex spot market API endpoints."""

    INSTRUMENT_INFO = "/api/pro/v1/cash/products"
    TICKER = "/api/pro/v1/spot/ticker"
    KLINE = "/api/pro/v1/barhist"
    ORDERBOOK = "/api/pro/v1/depth"
    PUBLIC_TRADE = "/api/pro/v1/trades"

    @property
    def hash(self) -> str:
        """Get the hash identifier for the endpoint."""
        return self.value.split("/")[-1]

    def __str__(self) -> str:
        return self.value
