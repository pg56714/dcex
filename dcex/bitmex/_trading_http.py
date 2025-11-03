"""
BitMEX Trading History HTTP client for execution and trade history operations.

This module provides functionality for retrieving trading history data from the BitMEX
exchange, including execution history, trade history, and trading volume information.
"""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trading import Trading


class TradingHTTP(HTTPManager):
    """
    BitMEX Trading History HTTP client for execution and trade history operations.

    This class provides methods for retrieving trading history data including
    execution history, trade history, and trading volume information.
    """

    def get_executions(
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
        targetAccountIds_array: list | None = None,
    ) -> dict[str, Any]:
        """
        Get execution history from the BitMEX exchange.

        Retrieves execution history with optional filtering and pagination.

        Args:
            product_symbol: Trading symbol to filter by
            filter: Filter criteria for executions
            columns: Specific columns to return
            count: Maximum number of results to return (default: 100)
            start: Starting index for pagination (default: 0)
            reverse: Whether to reverse the order of results (default: False)
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)
            targetAccountId: Target account ID
            targetAccountIds: Target account IDs as string
            targetAccountIds_array: Target account IDs as list

        Returns:
            Dictionary containing execution history

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

        res = self._request(
            method="GET",
            path=Trading.GET_EXECUTIONS,
            query=payload,
        )
        return res

    def get_trade_history(
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
        targetAccountIds_array: list | None = None,
    ) -> dict[str, Any]:
        """
        Get trade history from the BitMEX exchange.

        Retrieves trade history with optional filtering and pagination.

        Args:
            product_symbol: Trading symbol to filter by
            filter: Filter criteria for trades
            columns: Specific columns to return
            count: Maximum number of results to return (default: 100)
            start: Starting index for pagination (default: 0)
            reverse: Whether to reverse the order of results (default: False)
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)
            targetAccountId: Target account ID
            targetAccountIds: Target account IDs as string
            targetAccountIds_array: Target account IDs as list

        Returns:
            Dictionary containing trade history

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

        res = self._request(
            method="GET",
            path=Trading.GET_TRADE_HISTORY,
            query=payload,
        )
        return res

    def get_trading_volume(
        self,
    ) -> dict[str, Any]:
        """
        Get trading volume information from the BitMEX exchange.

        Retrieves trading volume data for the account.

        Returns:
            Dictionary containing trading volume information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        res = self._request(
            method="GET",
            path=Trading.GET_TRADING_VOLUME,
            query=payload,
        )
        return res
