"""OKX Market HTTP client for market data operations."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import Market


class MarketHTTP(HTTPManager):
    """HTTP client for OKX market data operations."""

    async def get_candles_ticks(
        self,
        product_symbol: str,
        bar: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get candlestick data.

        Args:
            product_symbol: Trading pair symbol
            bar: Bar size (1m, 3m, 5m, 15m, 30m, 1H, 2H, 4H, 6H, 12H, 1D, 1W, 1M, 3M, 6M, 1Y)
            after: Pagination parameter - records after this ID
            before: Pagination parameter - records before this ID
            limit: Number of results per request (max 300)

        Returns:
            Dict containing candlestick data
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if bar is not None:
            payload["bar"] = bar
        if after is not None:
            payload["after"] = after
        if before is not None:
            payload["before"] = before
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Market.GET_KLINE,
            query=payload,
            signed=False,
        )
        return res

    async def get_orderbook(
        self,
        product_symbol: str,
        sz: str | None = None,
    ) -> dict[str, Any]:
        """
        Get order book data.

        Args:
            product_symbol: Trading pair symbol
            sz: Number of results per request (max 400)

        Returns:
            Dict containing order book data
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if sz is not None:
            payload["sz"] = sz

        res = await self._request(
            method="GET",
            path=Market.GET_ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    async def get_tickers(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
    ) -> dict[str, Any]:
        """
        Get ticker data.

        Args:
            instType: Instrument type (SPOT, SWAP, FUTURES, OPTION)
            uly: Underlying asset
            instFamily: Instrument family

        Returns:
            Dict containing ticker data
        """
        payload = {
            "instType": instType,
        }
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily

        res = await self._request(
            method="GET",
            path=Market.GET_TICKERS,
            query=payload,
            signed=False,
        )
        return res

    async def get_public_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get public trades data.

        Args:
            product_symbol: Trading pair symbol
            limit: Number of results per request (max 500)

        Returns:
            Dict containing public trades data
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=Market.GET_PUBLIC_TRADES,
            query=payload,
            signed=False,
        )
        return res
