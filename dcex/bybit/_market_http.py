"""
Bybit Market HTTP client.

This module provides HTTP client functionality for market data operations
on the Bybit exchange, including instrument information, price data,
orderbook, and trading history.
"""

from typing import Any

from ..utils.common import Common
from ..utils.timeframe_utils import bybit_convert_timeframe
from ._http_manager import HTTPManager
from .endpoints.market import Market


class MarketHTTP(HTTPManager):
    """
    Bybit market data HTTP client.

    This class provides methods for interacting with Bybit's market data
    API endpoints, including:
    - Instrument information
    - Kline/candlestick data
    - Order book data
    - Ticker information
    - Funding rate history
    - Public trade history
    - Risk limit information

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    def get_instruments_info(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        status: str | None = None,
        baseCoin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get instruments information.

        Args:
            category: Instrument category (spot, linear, inverse, option)
            product_symbol: Optional product symbol to filter results
            status: Optional instrument status to filter results
            baseCoin: Optional base coin to filter results
            limit: Optional maximum number of results
            cursor: Optional cursor for pagination

        Returns:
            Dict containing instruments information
        """
        payload: dict[str, Any] = {
            "category": category,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if status is not None:
            payload["status"] = status
        if baseCoin is not None:
            payload["baseCoin"] = baseCoin
        if limit is not None:
            payload["limit"] = str(limit)
        if cursor is not None:
            payload["cursor"] = cursor

        res = self._request(
            method="GET",
            path=Market.GET_INSTRUMENTS_INFO,
            query=payload,
            signed=False,
        )
        return res

    def get_kline(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get kline/candlestick data.

        Args:
            product_symbol: Product symbol
            interval: Kline interval
            startTime: Optional start time timestamp
            limit: Optional maximum number of klines

        Returns:
            Dict containing kline data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "interval": bybit_convert_timeframe(interval),
        }
        if startTime is not None:
            payload["start"] = str(startTime)
        if limit is not None:
            payload["limit"] = str(limit)

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
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get order book data.

        Args:
            product_symbol: Product symbol
            limit: Optional maximum number of order book levels

        Returns:
            Dict containing order book data
        """
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=Market.GET_ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    def get_tickers(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get ticker information.

        Args:
            category: Instrument category (spot, linear, inverse, option)
            product_symbol: Optional product symbol to filter results
            baseCoin: Optional base coin to filter results

        Returns:
            Dict containing ticker information
        """
        payload = {
            "category": category,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if baseCoin is not None:
            payload["baseCoin"] = baseCoin

        res = self._request(
            method="GET",
            path=Market.GET_TICKERS,
            query=payload,
            signed=False,
        )
        return res

    def get_funding_rate_history(
        self,
        product_symbol: str,
        startTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get funding rate history.

        Args:
            product_symbol: Product symbol
            startTime: Optional start time timestamp
            limit: Optional maximum number of records

        Returns:
            Dict containing funding rate history
        """
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
        }
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=Market.GET_FUNDING_RATE_HISTORY,
            query=payload,
            signed=False,
        )
        return res

    def get_public_trade_history(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get public trade history.

        Args:
            product_symbol: Product symbol
            limit: Optional maximum number of trades

        Returns:
            Dict containing public trade history
        """
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=Market.GET_PUBLIC_TRADE_HISTORY,
            query=payload,
            signed=False,
        )
        return res

    def get_open_interest(
        self,
        product_symbol: str,
        intervalTime: str = "5min",
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get open interest history.

        Args:
            product_symbol: Product symbol.
            intervalTime: Interval time (5min, 15min, 30min, 1h, 4h, 1d).
            startTime: Optional start timestamp in milliseconds.
            endTime: Optional end timestamp in milliseconds.
            limit: Optional maximum number of records.
            cursor: Optional pagination cursor.

        Returns:
            Dict containing open interest data.
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
            "intervalTime": intervalTime,
        }
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if endTime is not None:
            payload["endTime"] = str(endTime)
        if limit is not None:
            payload["limit"] = str(limit)
        if cursor is not None:
            payload["cursor"] = cursor

        res = self._request(
            method="GET",
            path=Market.GET_OPEN_INTEREST,
            query=payload,
            signed=False,
        )
        return res

    def get_long_short_ratio(
        self,
        product_symbol: str,
        period: str = "5min",
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get long/short account ratio history.

        Args:
            product_symbol: Product symbol.
            period: Data recording period (5min, 15min, 30min, 1h, 4h, 1d).
            startTime: Optional start timestamp in milliseconds.
            endTime: Optional end timestamp in milliseconds.
            limit: Optional maximum number of records.
            cursor: Optional pagination cursor.

        Returns:
            Dict containing long/short ratio data.
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
            "period": period,
        }
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if endTime is not None:
            payload["endTime"] = str(endTime)
        if limit is not None:
            payload["limit"] = str(limit)
        if cursor is not None:
            payload["cursor"] = cursor

        res = self._request(
            method="GET",
            path=Market.GET_LONG_SHORT_RATIO,
            query=payload,
            signed=False,
        )
        return res

    def get_historical_volatility(
        self,
        category: str = "option",
        baseCoin: str | None = None,
        period: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """
        Get historical volatility data.

        Args:
            category: Instrument category.
            baseCoin: Optional base coin.
            period: Optional period.
            startTime: Optional start timestamp in milliseconds.
            endTime: Optional end timestamp in milliseconds.

        Returns:
            Dict containing historical volatility data.
        """
        payload: dict[str, Any] = {"category": category}
        if baseCoin is not None:
            payload["baseCoin"] = baseCoin
        if period is not None:
            payload["period"] = str(period)
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if endTime is not None:
            payload["endTime"] = str(endTime)

        res = self._request(
            method="GET",
            path=Market.GET_HISTORICAL_VOLATILITY,
            query=payload,
            signed=False,
        )
        return res

    def get_insurance_pool(self, coin: str | None = None) -> dict[str, Any]:
        """
        Get insurance pool data.

        Args:
            coin: Optional coin filter.

        Returns:
            Dict containing insurance pool data.
        """
        payload: dict[str, Any] = {}
        if coin is not None:
            payload["coin"] = coin

        res = self._request(
            method="GET",
            path=Market.GET_INSURANCE_POOL,
            query=payload,
            signed=False,
        )
        return res

    def get_delivery_price(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get delivery price data.

        Args:
            category: Instrument category.
            product_symbol: Optional product symbol.
            baseCoin: Optional base coin.
            limit: Optional maximum number of records.
            cursor: Optional pagination cursor.

        Returns:
            Dict containing delivery price data.
        """
        payload: dict[str, Any] = {"category": category}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if baseCoin is not None:
            payload["baseCoin"] = baseCoin
        if limit is not None:
            payload["limit"] = str(limit)
        if cursor is not None:
            payload["cursor"] = cursor

        res = self._request(
            method="GET",
            path=Market.GET_DELIVERY_PRICE,
            query=payload,
            signed=False,
        )
        return res

    def get_order_price_limit(
        self,
        product_symbol: str,
        category: str = "linear",
    ) -> dict[str, Any]:
        """
        Get order price limit data.

        Args:
            product_symbol: Product symbol.
            category: Instrument category.

        Returns:
            Dict containing order price limit data.
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol) or category,
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
        }

        res = self._request(
            method="GET",
            path=Market.GET_ORDER_PRICE_LIMIT,
            query=payload,
            signed=False,
        )
        return res

    def get_adl_alert(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get ADL alert data.

        Args:
            category: Instrument category.
            product_symbol: Optional product symbol.

        Returns:
            Dict containing ADL alert data.
        """
        payload: dict[str, Any] = {"category": category}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)

        res = self._request(
            method="GET",
            path=Market.GET_ADL_ALERT,
            query=payload,
            signed=False,
        )
        return res

    def get_risk_limit(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get risk limit information.

        Args:
            category: Instrument category (linear, inverse)
            product_symbol: Optional product symbol to filter results
            cursor: Optional cursor for pagination

        Returns:
            Dict containing risk limit information
        """
        payload = {"category": category}

        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)

        res = self._request(
            method="GET",
            path=Market.GET_RISK_MARKET,
            query=payload,
            signed=False,
        )
        return res
