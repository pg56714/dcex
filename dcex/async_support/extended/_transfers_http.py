"""Extended internal transfer endpoints."""

from collections.abc import Mapping
from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers between subaccounts of the same wallet."""

    async def submit_internal_transfer(self, body: Mapping[str, Any]) -> Any:  # noqa: ANN401
        """Submit a pre-signed transfer between subaccounts of the same wallet."""
        return await self._native_private(
            "submit_internal_transfer", self._native_params(body=dict(body))
        )
