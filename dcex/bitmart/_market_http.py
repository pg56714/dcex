"""Bitmart market data HTTP client."""

from typing import Any

from ..utils.common import Common
from ..utils.timeframe_utils import bitmart_convert_timeframe
from ._http_manager import HTTPManager
from .endpoints.market import FuturesMarket, SpotMarket


class MarketHTTP(HTTPManager):
    """
    Market data HTTP client for Bitmart.

    This class provides methods to access market data including
    currencies, trading pairs, tickers, klines, and futures data.
    """

    def get_spot_currencies(self) -> dict[str, Any]:
        """
        Get all available spot currencies.

        Returns:
            Dict containing spot currencies information

        Raises:
            FailedRequestError: If the API request fails
        """
        res = self._request(
            method="GET",
            path=SpotMarket.GET_SPOT_CURRENCIES,
            query=None,
            signed=False,
        )
        return res

    def get_trading_pairs(self) -> dict[str, Any]:
        """
        Get all available trading pairs.

        Returns:
            Dict containing trading pairs information

        Raises:
            FailedRequestError: If the API request fails
        """
        res = self._request(
            method="GET",
            path=SpotMarket.GET_TRADING_PAIRS,
            query=None,
            signed=False,
        )
        return res

    def get_trading_pairs_details(self) -> dict[str, Any]:
        """
        Get detailed information for all trading pairs.

        Returns:
            Dict containing detailed trading pairs information

        Raises:
            FailedRequestError: If the API request fails
        """
        res = self._request(
            method="GET",
            path=SpotMarket.GET_TRADING_PAIRS_DETAILS,
            query=None,
            signed=False,
        )
        return res

    def get_ticker_of_all_pairs(self) -> dict[str, Any]:
        """
        Get ticker information for all trading pairs.

        Returns:
            Dict containing ticker information for all pairs

        Raises:
            FailedRequestError: If the API request fails
        """
        res = self._request(
            method="GET",
            path=SpotMarket.GET_TICKER_OF_ALL_PAIRS,
            query=None,
            signed=False,
        )
        return res

    def get_ticker_of_a_pair(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get ticker information for a specific trading pair.

        Args:
            product_symbol: Trading pair symbol

        Returns:
            Dict containing ticker information for the specified pair

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SpotMarket.GET_TICKER_OF_A_PAIR,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_kline(
        self,
        product_symbol: str,
        interval: str,
        before: int | None = None,
        after: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get spot kline (candlestick) data for a trading pair.

        Args:
            product_symbol: Trading pair symbol
            interval: Time interval for kline data
            before: Start timestamp (optional)
            after: End timestamp (optional)
            limit: Maximum number of records (optional)

        Returns:
            Dict containing kline data

        Raises:
            FailedRequestError: If the API request fails
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

        res = self._request(
            method="GET",
            path=SpotMarket.GET_SPOT_KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_contracts_details(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get futures contract details.

        Args:
            product_symbol: Contract symbol (optional)

        Returns:
            Dict containing contract details

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)

        res = self._request(
            method="GET",
            path=FuturesMarket.GET_CONTRACTS_DETAILS,
            query=payload,
            signed=False,
        )
        return res

    def get_depth(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get order book depth for a futures contract.

        Args:
            product_symbol: Contract symbol

        Returns:
            Dict containing order book depth data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }

        res = self._request(
            method="GET",
            path=FuturesMarket.GET_DEPTH,
            query=payload,
            signed=False,
        )
        return res

    def get_contract_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int,
        end_time: int,
    ) -> dict[str, Any]:
        """
        Get futures contract kline data.

        Args:
            product_symbol: Contract symbol
            interval: Time interval for kline data
            start_time: Start timestamp
            end_time: End timestamp

        Returns:
            Dict containing contract kline data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "step": bitmart_convert_timeframe(interval),
            "start_time": start_time,
            "end_time": end_time,
        }

        res = self._request(
            method="GET",
            path=FuturesMarket.GET_CONTRACTS_KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_current_funding_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get current funding rate for a futures contract.

        Args:
            product_symbol: Contract symbol

        Returns:
            Dict containing current funding rate information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }

        res = self._request(
            method="GET",
            path=FuturesMarket.GET_CURRENT_FUNDING_RATE,
            query=payload,
            signed=False,
        )
        return res

    def get_funding_rate_history(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get funding rate history for a futures contract.

        Args:
            product_symbol: Contract symbol
            limit: Maximum number of records (optional)

        Returns:
            Dict containing funding rate history

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=FuturesMarket.GET_FUNDING_RATE_HISTORY,
            query=payload,
            signed=False,
        )
        return res
