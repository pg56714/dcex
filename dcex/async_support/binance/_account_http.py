from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import FuturesAccount, SpotAccount
from .enums import BinanceProductType


class AccountHTTP(HTTPManager):
    """HTTP client for Binance account-related API endpoints."""

    async def get_account_balance(
        self,
        market_type: str,
    ) -> dict:
        """
        Get account balance.

        Args:
            market_type: Market type ("spot" or "swap")

        Returns:
            dict: Account balance information
        """
        res = await self._request(
            method="GET",
            path=SpotAccount.ACCOUNT_BALANCE
            if market_type == BinanceProductType.SPOT
            else FuturesAccount.ACCOUNT_BALANCE,
            query={},
        )
        return res

    async def get_income_history(
        self,
        product_symbol: str | None = None,
        incomeType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get futures income history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            incomeType: Income type (TRANSFER, WELCOME_BONUS, REALIZED_PNL, FUNDING_FEE, etc.)
            startTime: Start time in milliseconds
            endTime: End time in milliseconds
            page: Page number for pagination
            limit: Number of records per page

        Returns:
            dict: Income history data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
        if incomeType is not None:
            payload["incomeType"] = incomeType
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if page is not None:
            payload["page"] = page
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=FuturesAccount.INCOME_HISTORY,
            query=payload,
        )
        return res
