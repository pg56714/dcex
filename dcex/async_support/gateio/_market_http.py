"""
Gate.io market data HTTP client module.

This module provides the MarketHTTP class for interacting with Gate.io's
market data API endpoints, including futures, delivery, and spot market
data such as contracts, order books, klines, and tickers.
"""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import DeliveryMarket, FutureMarket, SpotMarket


class MarketHTTP(HTTPManager):
    """
    Gate.io market data HTTP client.

    This class provides methods for interacting with Gate.io's market data
    API endpoints, including:
    - Futures contracts and market data
    - Delivery contracts and market data
    - Spot currency pairs and market data
    - Order books, klines, tickers, and funding rates

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def get_all_futures_contracts(
        self,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get all futures contracts.

        Args:
            ccy: Settlement currency (usdt or btc)
            limit: Optional maximum number of contracts
            offset: Optional offset for pagination

        Returns:
            Dict containing futures contracts information
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {}
        if limit:
            payload["limit"] = limit
        if offset:
            payload["offset"] = offset

        res = await self._request(
            method="GET",
            path=FutureMarket.GET_ALL_CONTRACTS,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    async def get_a_single_futures_contract(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
    ) -> dict[str, Any]:
        """
        Get a single futures contract information.

        Args:
            product_symbol: Product symbol
            ccy: Settlement currency (usdt or btc)

        Returns:
            Dict containing single futures contract information
        """
        path_params = {
            "settle": ccy,
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        res = await self._request(
            method="GET",
            path=FutureMarket.GET_A_SINGLE_CONTRACT,
            path_params=path_params,
            signed=False,
        )
        return res

    async def get_contract_order_book(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool = False,
    ) -> dict[str, Any]:
        """
        Get contract order book.

        Args:
            product_symbol: Product symbol
            ccy: Settlement currency (usdt or btc)
            path: Contract type (futures or delivery)
            interval: Optional order book interval
            limit: Optional maximum number of orders
            with_id: Whether to include order IDs

        Returns:
            Dict containing order book data
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if interval:
            payload["interval"] = interval
        if limit:
            payload["limit"] = limit
        if with_id:
            payload["with_id"] = with_id

        if path == "futures":
            path_ = FutureMarket.ORDER_BOOK
        elif path == "delivery":
            path_ = DeliveryMarket.ORDER_BOOK
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = await self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    async def get_contract_kline(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """
        Get contract kline/candlestick data.

        Args:
            product_symbol: Product symbol
            ccy: Settlement currency (usdt or btc)
            path: Contract type (futures or delivery)
            from_timestamp: Optional start time timestamp
            to_timestamp: Optional end time timestamp
            limit: Optional maximum number of klines
            interval: Optional kline interval

        Returns:
            Dict containing kline data
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if from_timestamp:
            payload["from"] = from_timestamp
        if to_timestamp:
            payload["to"] = to_timestamp
        if limit:
            payload["limit"] = limit
        if interval:
            payload["interval"] = interval

        if path == "futures":
            path_ = FutureMarket.GET_KLINE
        elif path == "delivery":
            path_ = DeliveryMarket.GET_KLINE
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = await self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    async def get_contract_list_tickers(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Get contract ticker information.

        Args:
            product_symbol: Product symbol
            ccy: Settlement currency (usdt or btc)
            path: Contract type (futures or delivery)

        Returns:
            Dict containing ticker information
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if path == "futures":
            path_ = FutureMarket.LIST_TICKERS
        elif path == "delivery":
            path_ = DeliveryMarket.LIST_TICKERS
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = await self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    async def get_futures_funding_rate_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """
        Get futures funding rate history.

        Args:
            product_symbol: Product symbol
            ccy: Settlement currency (usdt or btc)
            limit: Optional maximum number of records
            from_timestamp: Optional start time timestamp
            to_timestamp: Optional end time timestamp

        Returns:
            Dict containing funding rate history
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if limit:
            payload["limit"] = limit
        if from_timestamp:
            payload["from"] = from_timestamp
        if to_timestamp:
            payload["to"] = to_timestamp

        res = await self._request(
            method="GET",
            path=FutureMarket.FUNDING_RATE_HISTORY,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    async def get_all_delivery_contracts(self) -> dict[str, Any]:
        """
        Get all delivery contracts.

        Returns:
            Dict containing delivery contracts information
        """
        path_params = {
            "settle": "usdt",
        }

        res = await self._request(
            method="GET",
            path=DeliveryMarket.GET_ALL_CONTRACTS,
            path_params=path_params,
            signed=False,
        )
        return res

    async def get_spot_all_currency_pairs(self) -> dict[str, Any]:
        """
        Get all spot currency pairs.

        Returns:
            Dict containing spot currency pairs information
        """
        res = await self._request(
            method="GET",
            path=SpotMarket.GET_ALL_CURRENCY_PAIRS,
            signed=False,
        )
        return res

    async def get_spot_order_book(
        self,
        product_symbol: str,
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool = False,
    ) -> dict[str, Any]:
        """
        Get spot order book.

        Args:
            product_symbol: Product symbol
            interval: Optional order book interval
            limit: Optional maximum number of orders
            with_id: Whether to include order IDs

        Returns:
            Dict containing spot order book data
        """
        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if interval:
            payload["interval"] = interval
        if limit:
            payload["limit"] = limit
        if with_id:
            payload["with_id"] = with_id

        res = await self._request(
            method="GET",
            path=SpotMarket.ORDER_BOOK,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_kline(
        self,
        product_symbol: str,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot kline/candlestick data.

        Args:
            product_symbol: Product symbol
            from_timestamp: Optional start time timestamp
            to_timestamp: Optional end time timestamp
            limit: Optional maximum number of klines
            interval: Optional kline interval

        Returns:
            Dict containing spot kline data
        """
        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if from_timestamp:
            payload["from"] = from_timestamp
        if to_timestamp:
            payload["to"] = to_timestamp
        if limit:
            payload["limit"] = limit
        if interval:
            payload["interval"] = interval

        res = await self._request(
            method="GET",
            path=SpotMarket.GET_KLINE,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_list_tickers(
        self,
        product_symbol: str,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot ticker information.

        Args:
            product_symbol: Product symbol
            timezone: Optional timezone for timestamps

        Returns:
            Dict containing spot ticker information
        """

        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if timezone:
            payload["timezone"] = timezone

        res = await self._request(
            method="GET",
            path=SpotMarket.LIST_TICKERS,
            query=payload,
            signed=False,
        )
        return res
