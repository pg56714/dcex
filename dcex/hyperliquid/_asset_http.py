"""Asset-related HTTP API client for Hyperliquid exchange."""

from typing import Any

from ._http_manager import HTTPManager
from .endpoint.asset import Asset
from .endpoint.path import Path


class AssetHTTP(HTTPManager):
    """HTTP client for asset-related operations on Hyperliquid exchange."""

    def user_vault_equities(
        self,
        user: str,
    ) -> dict[str, Any]:
        """
        Get user vault equities.

        Args:
            user: Wallet address

        Returns:
            Dict containing user vault equities information
        """
        payload = {
            "type": Asset.USERVAULTEQUITIES,
            "user": user,
        }

        res = self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res
