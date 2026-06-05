"""KuCoin Spot Account HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import FuturesAccount, SpotAccount


class AccountHTTP(HTTPManager):
    """
    HTTP client for KuCoin Spot Account API operations.

    This class provides methods for retrieving account information,
    including balance details and account management operations.
    """

    def get_account_balance(
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

        res = self._request(
            method="GET",
            path=SpotAccount.ACCOUNT_BALANCE,
            query=payload,
        )
        return res

    def get_futures_account(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures account overview."""
        payload: dict[str, Any] = {}
        if currency:
            payload["currency"] = currency

        res = self._request(
            method="GET",
            path=FuturesAccount.ACCOUNT_OVERVIEW,
            query=payload,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_positions(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures positions."""
        payload: dict[str, Any] = {}
        if currency:
            payload["currency"] = currency

        res = self._request(
            method="GET",
            path=FuturesAccount.POSITIONS,
            query=payload,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_position(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve one KuCoin futures position."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }

        res = self._request(
            method="GET",
            path=FuturesAccount.POSITION,
            query=payload,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_position_mode(self) -> dict[str, Any]:
        """Retrieve KuCoin futures position mode."""
        res = self._request(
            method="GET",
            path=FuturesAccount.POSITION_MODE,
            base_url=self.futures_base_url,
        )
        return res
