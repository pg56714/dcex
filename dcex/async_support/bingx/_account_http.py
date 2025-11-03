"""BingX account HTTP client."""

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import SwapAccount


class AccountHTTP(HTTPManager):
    """HTTP client for BingX account-related API endpoints."""

    async def get_account_balance(self) -> dict:
        """
        Get account balance information.

        Returns:
            dict: Account balance data
        """
        payload = {}
        res = await self._request(
            method="GET",
            path=SwapAccount.ACCOUNT_BALANCE,
            query=payload,
        )
        return res

    async def get_open_positions(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get open positions.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Open positions data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)

        res = await self._request(
            method="GET",
            path=SwapAccount.OPEN_POSITIONS,
            query=payload,
        )
        return res

    async def get_fund_flow(
        self,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get fund flow history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            income_type: Income type (TRANSFER_IN, TRANSFER_OUT, TRADE_FEE, etc.)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of records per page

        Returns:
            dict: Fund flow history data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = product_symbol
        if income_type is not None:
            payload["incomeType"] = income_type
        if start_time is not None:
            payload["startTime"] = start_time
        if end_time is not None:
            payload["endTime"] = end_time
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=SwapAccount.FUND_FLOW,
            query=payload,
        )
        return res

    async def get_listen_key(self) -> str:
        """
        Get WebSocket listen key.

        Returns:
            str: WebSocket listen key
        """

        if self.session is None or getattr(self.session, "is_closed", False):
            await self.async_init()
        if self.session is None:
            raise ValueError("Session is not initialized")
        if not self.api_key:
            raise ValueError("API key is required")

        url = self.base_url + SwapAccount.LISTEN_KEY
        headers = {"X-BX-APIKEY": self.api_key}

        res = await self.session.post(url, headers=headers)
        data = res.json()
        return data.get("listenKey")

    async def keep_alive_listen_key(self, listen_key: str) -> dict:
        """
        Keep alive WebSocket listen key.

        Args:
            listen_key: WebSocket listen key to keep alive

        Returns:
            dict: API response
        """
        payload = {
            "listenKey": listen_key,
        }

        res = await self._request(
            method="PUT",
            path=SwapAccount.LISTEN_KEY,
            query=payload,
        )
        return res
