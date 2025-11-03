from typing import Any

import msgspec

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import Market


class MarketHTTP(HTTPManager):
    """
    HTTP client for BitMEX market data API endpoints.

    This class provides methods to retrieve market data from BitMEX,
    including instrument information, orderbook, trades, tickers, and klines.
    """

    async def get_instrument_info(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """
        Get instrument information for trading pairs.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            filter: Filter criteria as a dictionary
            count: Maximum number of results to return

        Returns:
            dict: Instrument information data

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

        res = await self._request(
            method="GET",
            path=Market.INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_orderbook(
        self,
        product_symbol: str,
        depth: int | None = None,
    ) -> dict[str, Any]:
        """
        Get orderbook data for a specific trading pair.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            depth: Number of price levels to return

        Returns:
            dict: Orderbook data with bids and asks

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol),
        }
        if depth is not None:
            payload["depth"] = depth

        res = await self._request(
            method="GET",
            path=Market.ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    async def get_trades(
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
        Get recent trade data.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            filter: Filter criteria as a dictionary
            columns: Comma-separated list of columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)

        Returns:
            dict: Trade data

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

        res = await self._request(
            method="GET",
            path=Market.TRADE,
            query=payload,
            signed=False,
        )
        return res

    async def get_ticker(
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
            binSize: Time interval for ticker data
            partial: Whether to include partial data
            symbol: Trading symbol (e.g., 'BTCUSD')
            filter: Filter criteria as a dictionary
            columns: Comma-separated list of columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)

        Returns:
            dict: Ticker data

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

        res = await self._request(
            method="GET",
            path=Market.TICKER,
            query=payload,
            signed=False,
        )
        return res

    async def get_kline(
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
        Get kline/candlestick data for trading pairs.

        Args:
            binSize: Time interval for kline data (e.g., '1m', '5m', '1h')
            partial: Whether to include partial data
            symbol: Trading symbol (e.g., 'BTCUSD')
            filter: Filter criteria as a dictionary
            columns: Comma-separated list of columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)

        Returns:
            dict: Kline/candlestick data

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

        res = await self._request(
            method="GET",
            path=Market.KLINE,
            query=payload,
            signed=False,
        )
        return res

    async def get_funding(
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
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            filter: Filter criteria as a dictionary
            columns: Comma-separated list of columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)

        Returns:
            dict: Funding rate data

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

        res = await self._request(
            method="GET",
            path=Market.FUNDING,
            query=payload,
            signed=False,
        )
        return res
