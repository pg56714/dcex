"""
Zoomex account management HTTP client module.

This module provides the AccountHTTP class for interacting with Zoomex's
account management API endpoints, including wallet balance queries.
"""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import Account


class AccountHTTP(HTTPManager):
    """
    Zoomex account management HTTP client.

    This class provides methods for interacting with Zoomex's account management
    API endpoints, including:
    - Wallet balance queries

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def get_wallet_balance(self, product_symbol: str | None = None) -> dict[str, Any]:
        """
        Get wallet balance for CONTRACT account.

        Args:
            product_symbol: Optional product symbol to filter balance for specific coin

        Returns:
            Dict containing wallet balance information
        """
        payload: dict[str, Any] = {
            "accountType": "CONTRACT",
        }
        if product_symbol is not None:
            payload["coin"] = self.ptm.get_exchange_symbol(Common.ZOOMEX, product_symbol)

        res = await self._request(
            method="GET",
            path=Account.GET_WALLET_BALANCE,
            query=payload,
            signed=True,
        )
        return res
