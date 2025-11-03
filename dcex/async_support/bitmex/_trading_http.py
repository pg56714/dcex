from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trading import Trading


class TradingHTTP(HTTPManager):
    """
    HTTP client for BitMEX trading history API endpoints.

    This class provides methods to retrieve trading history and execution data
    from BitMEX, including execution history, trade history, and trading volume.
    """

    async def get_executions(
        self,
        product_symbol: str | None = None,
        filter: str | None = None,
        columns: str | None = None,
        count: int = 100,
        start: int = 0,
        reverse: bool = False,
        startTime: str | None = None,
        endTime: str | None = None,
        targetAccountId: int | None = None,
        targetAccountIds: str | None = None,
        targetAccountIds_array: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get execution history.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            filter: Filter criteria as a string
            columns: Comma-separated list of columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)
            targetAccountId: Account ID to query
            targetAccountIds: Account IDs as a string
            targetAccountIds_array: List of account IDs

        Returns:
            dict: Execution history data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        if filter is not None:
            payload["filter"] = filter
        if columns is not None:
            payload["columns"] = columns
        if count is not None:
            payload["count"] = count
        if start is not None:
            payload["start"] = start
        if reverse is not None:
            payload["reverse"] = reverse
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if targetAccountId is not None:
            payload["targetAccountId"] = targetAccountId
        if targetAccountIds is not None:
            payload["targetAccountIds"] = targetAccountIds
        if targetAccountIds_array is not None:
            payload["targetAccountIds[]"] = targetAccountIds_array

        res = await self._request(
            method="GET",
            path=Trading.GET_EXECUTIONS,
            query=payload,
        )
        return res

    async def get_trade_history(
        self,
        product_symbol: str | None = None,
        filter: str | None = None,
        columns: str | None = None,
        count: int = 100,
        start: int = 0,
        reverse: bool = False,
        startTime: str | None = None,
        endTime: str | None = None,
        targetAccountId: int | None = None,
        targetAccountIds: str | None = None,
        targetAccountIds_array: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get trade history.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            filter: Filter criteria as a string
            columns: Comma-separated list of columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)
            targetAccountId: Account ID to query
            targetAccountIds: Account IDs as a string
            targetAccountIds_array: List of account IDs

        Returns:
            dict: Trade history data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        if filter is not None:
            payload["filter"] = filter
        if columns is not None:
            payload["columns"] = columns
        if count is not None:
            payload["count"] = count
        if start is not None:
            payload["start"] = start
        if reverse is not None:
            payload["reverse"] = reverse
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if targetAccountId is not None:
            payload["targetAccountId"] = targetAccountId
        if targetAccountIds is not None:
            payload["targetAccountIds"] = targetAccountIds
        if targetAccountIds_array is not None:
            payload["targetAccountIds[]"] = targetAccountIds_array

        res = await self._request(
            method="GET",
            path=Trading.GET_TRADE_HISTORY,
            query=payload,
        )
        return res

    async def get_trading_volume(
        self,
    ) -> dict[str, Any]:
        """
        Get trading volume information.

        Returns:
            dict: Trading volume data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        res = await self._request(
            method="GET",
            path=Trading.GET_TRADING_VOLUME,
            query=payload,
        )
        return res
