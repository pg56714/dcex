from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import DeliveryMarket, FutureMarket, SpotMarket


class MarketHTTP(HTTPManager):
    """
    Gate.io Market HTTP client for market data operations.

    This class provides methods for retrieving market data including
    contract information, order books, klines, tickers, and funding rates
    for spot, futures, and delivery markets.
    """

    def get_all_futures_contracts(
        self,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get all futures contracts for a settlement currency.

        Args:
            ccy: Settlement currency, either "usdt" or "btc"
            limit: Maximum number of contracts to return
            offset: Number of contracts to skip

        Returns:
            dict[str, Any]: List of futures contracts with their specifications
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {}
        if limit:
            payload["limit"] = limit
        if offset:
            payload["offset"] = offset

        res = self._request(
            method="GET",
            path=FutureMarket.GET_ALL_CONTRACTS,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    def get_a_single_futures_contract(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
    ) -> dict[str, Any]:
        """
        Get information for a single futures contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"

        Returns:
            dict[str, Any]: Contract information including specifications and status
        """
        path_params = {
            "settle": ccy,
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        res = self._request(
            method="GET",
            path=FutureMarket.GET_A_SINGLE_CONTRACT,
            path_params=path_params,
            signed=False,
        )
        return res

    def get_contract_order_book(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool = False,
    ) -> dict[str, Any]:
        """
        Get order book for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"
            interval: Order book precision interval
            limit: Maximum number of orders to return
            with_id: Whether to include order IDs

        Returns:
            dict[str, Any]: Order book data with bids and asks
        """
        path_params: dict[str, Any] = {
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

        res = self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    def get_contract_kline(
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
        Get kline/candlestick data for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"
            from_timestamp: Start timestamp in milliseconds
            to_timestamp: End timestamp in milliseconds
            limit: Maximum number of klines to return
            interval: Kline interval (e.g., "1m", "5m", "1h")

        Returns:
            dict[str, Any]: Kline data with OHLCV information
        """
        path_params: dict[str, Any] = {
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

        res = self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    def get_contract_list_tickers(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Get ticker information for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Ticker data with price and volume information
        """
        path_params = {
            "settle": ccy,
        }

        payload = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if path == "futures":
            path_ = FutureMarket.LIST_TICKERS
        elif path == "delivery":
            path_ = DeliveryMarket.LIST_TICKERS
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    def get_futures_funding_rate_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """
        Get funding rate history for a futures contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            limit: Maximum number of records to return
            from_timestamp: Start timestamp in milliseconds
            to_timestamp: End timestamp in milliseconds

        Returns:
            dict[str, Any]: Funding rate history data
        """
        path_params: dict[str, Any] = {
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

        res = self._request(
            method="GET",
            path=FutureMarket.FUNDING_RATE_HISTORY,
            path_params=path_params,
            query=payload,
            signed=False,
        )
        return res

    def get_all_delivery_contracts(self) -> dict[str, Any]:
        """
        Get all delivery contracts.

        Returns:
            dict[str, Any]: List of delivery contracts with their specifications
        """
        path_params = {
            "settle": "usdt",
        }

        res = self._request(
            method="GET",
            path=DeliveryMarket.GET_ALL_CONTRACTS,
            path_params=path_params,
            signed=False,
        )
        return res

    def get_spot_all_currency_pairs(self) -> dict[str, Any]:
        """
        Get all spot currency pairs.

        Returns:
            dict[str, Any]: List of spot currency pairs with their specifications
        """
        res = self._request(
            method="GET",
            path=SpotMarket.GET_ALL_CURRENCY_PAIRS,
            signed=False,
        )
        return res

    def get_spot_order_book(
        self,
        product_symbol: str,
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool = False,
    ) -> dict[str, Any]:
        """
        Get order book for a spot currency pair.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            interval: Order book precision interval
            limit: Maximum number of orders to return
            with_id: Whether to include order IDs

        Returns:
            dict[str, Any]: Spot order book data with bids and asks
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

        res = self._request(
            method="GET",
            path=SpotMarket.ORDER_BOOK,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_kline(
        self,
        product_symbol: str,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """
        Get kline/candlestick data for a spot currency pair.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            from_timestamp: Start timestamp in milliseconds
            to_timestamp: End timestamp in milliseconds
            limit: Maximum number of klines to return
            interval: Kline interval (e.g., "1m", "5m", "1h")

        Returns:
            dict[str, Any]: Spot kline data with OHLCV information
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

        res = self._request(
            method="GET",
            path=SpotMarket.GET_KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_list_tickers(
        self,
        product_symbol: str,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """
        Get ticker information for a spot currency pair.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            timezone: Timezone for timestamp formatting

        Returns:
            dict[str, Any]: Spot ticker data with price and volume information
        """

        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if timezone:
            payload["timezone"] = timezone

        res = self._request(
            method="GET",
            path=SpotMarket.LIST_TICKERS,
            query=payload,
            signed=False,
        )
        return res
