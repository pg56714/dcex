"""Asset-related API endpoints for Hyperliquid exchange."""

from enum import Enum


class Asset(str, Enum):
    """
    Asset-related API endpoints for Hyperliquid exchange.

    This enum defines all asset-related API endpoints including user vault equities.
    """

    USERVAULTEQUITIES = "userVaultEquities"

    def __str__(self) -> str:
        return self.value
