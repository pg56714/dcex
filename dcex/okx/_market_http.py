from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import Market


class MarketHTTP(HTTPManager):
    def get_candles_ticks(
        self,
        product_symbol: str,
        bar: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get candlestick data for a trading pair.

        Args:
            product_symbol: Trading pair symbol
            bar: Bar size (e.g., "1m", "5m", "1H", "1D")
            after: Pagination parameter - timestamp after this value
            before: Pagination parameter - timestamp before this value
            limit: Number of results to return (max 300)

        Returns:
            Dictionary containing candlestick data.
        """
        payload: dict[str, Any] = {
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

        res = self._request(
            method="GET",
            path=Market.GET_KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_orderbook(
        self,
        product_symbol: str,
        sz: str | None = None,
    ) -> dict[str, Any]:
        """
        Get order book data for a trading pair.

        Args:
            product_symbol: Trading pair symbol
            sz: Number of results to return (max 400)

        Returns:
            Dictionary containing order book data.
        """
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if sz is not None:
            payload["sz"] = sz

        res = self._request(
            method="GET",
            path=Market.GET_ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    def get_tickers(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
    ) -> dict[str, Any]:
        """
        Get ticker information for instruments.

        Args:
            instType: Instrument type (SPOT, SWAP, FUTURES, OPTION)
            uly: Underlying asset symbol
            instFamily: Instrument family

        Returns:
            Dictionary containing ticker information.
        """
        payload: dict[str, Any] = {
            "instType": instType,
        }
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily

        res = self._request(
            method="GET",
            path=Market.GET_TICKERS,
            query=payload,
            signed=False,
        )
        return res

    def get_public_trades(
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

        res = self._request(
            method="GET",
            path=Market.GET_PUBLIC_TRADES,
            query=payload,
            signed=False,
        )
        return res
