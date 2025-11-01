from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import FuturesMarket, SpotMarket
from .enums import BinanceProductType


class MarketHTTP(HTTPManager):
    """HTTP client for Binance market data API endpoints."""

    def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        product_symbols: list[str] | None = None,
        symbolStatus: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot trading exchange information from Binance.

        Args:
            product_symbol: Single trading pair symbol (e.g., 'BTCUSDT').
            product_symbols: List of trading pair symbols.
            symbolStatus: Filter symbols by trading status. Valid values:
                TRADING, HALT, BREAK. Cannot be used with symbols or symbol.

        Returns:
            dict[str, Any]: Exchange information including trading rules and symbols.

        Raises:
            FailedRequestError: If the API request fails.
        """
        payload: dict[str, Any] = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
        if product_symbols is not None:
            formatted_symbols = [
                self.ptm.get_exchange_symbol(Common.BINANCE, symbol) for symbol in product_symbols
            ]
            payload["symbols"] = str(formatted_symbols).replace("'", '"')
        if symbolStatus is not None:
            payload["symbolStatus"] = symbolStatus

        res = self._request(
            method="GET",
            path=SpotMarket.EXCHANGE_INFO,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get spot order book data from Binance.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT').
            limit: Number of orders to return (max: 5000, default: 100).

        Returns:
            dict[str, Any]: Order book data with bids and asks.

        Raises:
            FailedRequestError: If the API request fails.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)
        res = self._request(
            method="GET",
            path=SpotMarket.ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get recent spot trades from Binance.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT').
            limit: Number of trades to return (max: 1000, default: 500).

        Returns:
            dict[str, Any]: Recent trades data.

        Raises:
            FailedRequestError: If the API request fails.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SpotMarket.TRADES,
            query=payload,
            signed=False,
        )
        return res

    def get_klines(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get kline/candlestick data from Binance.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT').
            interval: Kline interval (e.g., '1m', '5m', '1h', '1d').
            start_time: Start time in milliseconds since epoch.
            limit: Number of klines to return (max: 1500, default: 500).

        Returns:
            dict[str, Any]: Kline data with OHLCV information.

        Raises:
            FailedRequestError: If the API request fails.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
            "interval": interval,
        }
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SpotMarket.KLINES
            if self.ptm.get_exchange_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesMarket.KLINES,
            query=payload,
            signed=False,
        )
        return res

    def get_futures_exchange_info(self) -> dict[str, Any]:
        """
        Get futures trading exchange information from Binance.

        Returns:
            dict[str, Any]: Futures exchange information including trading rules and symbols.

        Raises:
            FailedRequestError: If the API request fails.
        """
        res = self._request(
            method="GET",
            path=FuturesMarket.EXCHANGE_INFO,
            query=None,
            signed=False,
        )
        return res

    def get_futures_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get futures ticker data from Binance.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT'). If None, returns all symbols.

        Returns:
            dict[str, Any]: Ticker data with price and volume information.

        Raises:
            FailedRequestError: If the API request fails.
        """
        payload: dict[str, Any] = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)

        res = self._request(
            method="GET",
            path=FuturesMarket.BOOK_TICKER,
            query=payload,
            signed=False,
        )
        return res

    def get_futures_premium_index(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get futures premium index data from Binance.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT'). If None, returns all symbols.

        Returns:
            dict[str, Any]: Premium index data.

        Raises:
            FailedRequestError: If the API request fails.
        """
        payload: dict[str, Any] = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)

        res = self._request(
            method="GET",
            path=FuturesMarket.PREMIUM_INDEX,
            query=payload,
            signed=False,
        )
        return res

    def get_futures_funding_rate(
        self,
        product_symbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get futures funding rate history from Binance.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT').
            startTime: Start time in milliseconds since epoch.
            endTime: End time in milliseconds since epoch.
            limit: Number of records to return (max: 1000, default: 100).

        Returns:
            dict[str, Any]: Funding rate history data.

        Raises:
            FailedRequestError: If the API request fails.
        """
        payload: dict[str, Any] = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if endTime is not None:
            payload["endTime"] = str(endTime)
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=FuturesMarket.FUNDING_RATE_HISTORY,
            query=payload,
            signed=False,
        )
        return res
