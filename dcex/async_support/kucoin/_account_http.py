"""KuCoin Spot Account HTTP client."""

from typing import Any

from ._http_manager import HTTPManager
from .endpoints.account import SpotAccount


class AccountHTTP(HTTPManager):
    """
    HTTP client for KuCoin Spot Account API operations.

    This class provides methods for retrieving account information,
    including balance details and account management operations.
    """

    async def get_account_balance(
        self,
        currency: str | None = None,
        type: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve account balance information.

        Args:
            currency: Optional currency filter (e.g., "BTC", "USDT").
            type: Optional account type filter (e.g., "main", "trade").

        Returns:
            Account balance information from KuCoin API.
        """
        payload: dict[str, Any] = {}
        if currency:
            payload["currency"] = currency
        if type:
            payload["type"] = type

        res = await self._request(
            method="GET",
            path=SpotAccount.ACCOUNT_BALANCE,
            query=payload,
        )
        return res
