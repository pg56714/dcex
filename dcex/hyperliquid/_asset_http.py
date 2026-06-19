"""Asset-related HTTP API client for Hyperliquid exchange backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AssetHTTP(HTTPManager):
    """HTTP client for asset-related operations on Hyperliquid exchange."""

    def user_vault_equities(self, user: str) -> dict[str, Any]:
        """Get user vault equities."""
        return self._native_public(
            "user_vault_equities",
            self._native_params(user=user),
        )
