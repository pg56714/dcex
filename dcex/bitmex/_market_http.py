from typing import Any

import msgspec

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import Market


class MarketHTTP(HTTPManager):
    """
    BitMEX Market HTTP client for market data operations.

    This class provides methods for retrieving market data including
    instrument information, orderbook, trades, tickers, klines, and funding data.
    """

    def get_instrument_info(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """
        Get instrument information for trading pairs.

        Args:
            product_symbol: Trading symbol to filter by
            filter: Additional filter criteria as a dictionary
            count: Maximum number of results to return

        Returns:
            Dict containing instrument information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        if filter is not None:
            payload["filter"] = msgspec.json.encode(filter).decode("utf-8")
        if count is not None:
            payload["count"] = count

        res = self._request(
            method="GET",
            path=Market.INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    def get_orderbook(
        self,
        product_symbol: str,
        depth: int | None = None,
    ) -> dict[str, Any]:
        """
        Get orderbook data for a trading pair.

        Args:
            product_symbol: Trading symbol to get orderbook for
            depth: Number of price levels to return

        Returns:
            Dict containing orderbook data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol),
        }
        if depth is not None:
            payload["depth"] = depth

        res = self._request(
            method="GET",
            path=Market.ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    def get_trades(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """
        Get recent trades for trading pairs.

        Args:
            product_symbol: Trading symbol to filter by
            filter: Additional filter criteria as a dictionary
            columns: Specific columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)

        Returns:
            Dict containing trade data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        if filter is not None:
            payload["filter"] = str(filter)
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

        res = self._request(
            method="GET",
            path=Market.TRADE,
            query=payload,
            signed=False,
        )
        return res

    def get_ticker(
        self,
        binSize: str | None = None,
        partial: bool | None = None,
        symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """
        Get ticker data for trading pairs.

        Args:
            binSize: Time interval for bucketed data
            partial: Whether to include partial data
            symbol: Trading symbol to filter by
            filter: Additional filter criteria as a dictionary
            columns: Specific columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)

        Returns:
            Dict containing ticker data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}
        if binSize is not None:
            payload["binSize"] = binSize
        if partial is not None:
            payload["partial"] = partial
        if symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, symbol)
        if filter is not None:
            payload["filter"] = str(filter)
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

        res = self._request(
            method="GET",
            path=Market.TICKER,
            query=payload,
            signed=False,
        )
        return res

    def get_kline(
        self,
        binSize: str | None = None,
        partial: bool | None = None,
        symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """
        Get candlestick/kline data for trading pairs.

        Args:
            binSize: Time interval for bucketed data
            partial: Whether to include partial data
            symbol: Trading symbol to filter by
            filter: Additional filter criteria as a dictionary
            columns: Specific columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)

        Returns:
            Dict containing kline data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}
        if binSize is not None:
            payload["binSize"] = binSize
        if partial is not None:
            payload["partial"] = partial
        if symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, symbol)
        if filter is not None:
            payload["filter"] = str(filter)
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

        res = self._request(
            method="GET",
            path=Market.KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_funding(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """
        Get funding rate data for perpetual contracts.

        Args:
            product_symbol: Trading symbol to filter by
            filter: Additional filter criteria as a dictionary
            columns: Specific columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)

        Returns:
            Dict containing funding data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        if filter is not None:
            payload["filter"] = str(filter)
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

        res = self._request(
            method="GET",
            path=Market.FUNDING,
            query=payload,
            signed=False,
        )
        return res
