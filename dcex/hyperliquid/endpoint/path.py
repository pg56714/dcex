"""API path endpoints for Hyperliquid exchange."""

from enum import Enum


class Path(str, Enum):
    """
    API path endpoints for Hyperliquid exchange.

    This enum defines the basic API paths for information and exchange operations.
    """

    INFO = "/info"
    EXCHANGE = "/exchange"

    def __str__(self) -> str:
        return self.value
