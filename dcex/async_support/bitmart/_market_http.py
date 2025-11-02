from typing import Any

from ...utils.common import Common
from ...utils.timeframe_utils import bitmart_convert_timeframe
from ._http_manager import HTTPManager
from .endpoints.market import FuturesMarket, SpotMarket


class MarketHTTP(HTTPManager):
    """HTTP client for BitMart market-related API endpoints."""

    async def get_spot_currencies(self) -> dict[str, Any]:
        """
        Get spot currencies.

        Returns:
            dict: Spot currencies data
        """
        res = await self._request(
            method="GET",
            path=SpotMarket.GET_SPOT_CURRENCIES,
            query=None,
            signed=False,
        )
        return res

    async def get_trading_pairs(self) -> dict[str, Any]:
        """
        Get trading pairs.

        Returns:
            dict: Trading pairs data
        """
        res = await self._request(
            method="GET",
            path=SpotMarket.GET_TRADING_PAIRS,
            query=None,
            signed=False,
        )
        return res

    async def get_trading_pairs_details(self) -> dict[str, Any]:
        """
        Get trading pairs details.

        Returns:
            dict: Trading pairs details data
        """
        res = await self._request(
            method="GET",
            path=SpotMarket.GET_TRADING_PAIRS_DETAILS,
            query=None,
            signed=False,
        )
        return res

    async def get_ticker_of_all_pairs(self) -> dict[str, Any]:
        """
        Get ticker of all pairs.

        Returns:
            dict: Ticker data for all pairs
        """
        res = await self._request(
            method="GET",
            path=SpotMarket.GET_TICKER_OF_ALL_PAIRS,
            query=None,
            signed=False,
        )
        return res

    async def get_ticker_of_a_pair(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get ticker of a specific pair.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Ticker data for the pair
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }

        res = await self._request(
            method="GET",
            path=SpotMarket.GET_TICKER_OF_A_PAIR,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_kline(
        self,
        product_symbol: str,
        interval: str,
        before: int | None = None,
        after: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get spot kline data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            interval: Kline interval
            before: Before timestamp
            after: After timestamp
            limit: Number of klines to return

        Returns:
            dict: Spot kline data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if interval is not None:
            payload["step"] = str(bitmart_convert_timeframe(interval))
        if before is not None:
            payload["before"] = str(before)
        if after is not None:
            payload["after"] = str(after)
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=SpotMarket.GET_SPOT_KLINE,
            query=payload,
            signed=False,
        )
        return res

    async def get_contracts_details(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get contracts details.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Contracts details data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)

        res = await self._request(
            method="GET",
            path=FuturesMarket.GET_CONTRACTS_DETAILS,
            query=payload,
            signed=False,
        )
        return res

    async def get_depth(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get order book depth.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Order book depth data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }

        res = await self._request(
            method="GET",
            path=FuturesMarket.GET_DEPTH,
            query=payload,
            signed=False,
        )
        return res

    async def get_contract_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int,
        end_time: int,
    ) -> dict[str, Any]:
        """
        Get contract kline data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            interval: Kline interval
            start_time: Start time in milliseconds
            end_time: End time in milliseconds

        Returns:
            dict: Contract kline data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "step": bitmart_convert_timeframe(interval),
            "start_time": start_time,
            "end_time": end_time,
        }

        res = await self._request(
            method="GET",
            path=FuturesMarket.GET_CONTRACTS_KLINE,
            query=payload,
            signed=False,
        )
        return res

    async def get_current_funding_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get current funding rate.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Current funding rate data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }

        res = await self._request(
            method="GET",
            path=FuturesMarket.GET_CURRENT_FUNDING_RATE,
            query=payload,
            signed=False,
        )
        return res

    async def get_funding_rate_history(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get funding rate history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            limit: Number of records to return

        Returns:
            dict: Funding rate history data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=FuturesMarket.GET_FUNDING_RATE_HISTORY,
            query=payload,
            signed=False,
        )
        return res
