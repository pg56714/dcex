"""Aster V3 public market-data HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import FuturesMarket, SpotMarket


class MarketHTTP(HTTPManager):
    """HTTP client for Aster V3 public market APIs."""

    def _symbol(self, product_symbol: str) -> str:
        if "-" not in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.ASTER, product_symbol)

    def ping_spot(self) -> dict[str, Any] | list[Any]:
        """Test Aster spot API connectivity."""
        return self._request("GET", SpotMarket.PING, signed=False)

    def ping_futures(self) -> dict[str, Any] | list[Any]:
        """Test Aster futures API connectivity."""
        return self._request("GET", FuturesMarket.PING, signed=False)

    def get_spot_server_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot server time."""
        return self._request("GET", SpotMarket.SERVER_TIME, signed=False)

    def get_futures_server_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures server time."""
        return self._request("GET", FuturesMarket.SERVER_TIME, signed=False)

    def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot trading specifications."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request(
            "GET",
            SpotMarket.EXCHANGE_INFO,
            {"symbol": symbol, "symbols": symbols},
            signed=False,
        )

    def get_futures_exchange_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures trading specifications."""
        return self._request("GET", FuturesMarket.EXCHANGE_INFO, signed=False)

    def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot order-book depth."""
        return self._request(
            "GET",
            SpotMarket.DEPTH,
            {"symbol": self._symbol(product_symbol), "limit": limit},
            signed=False,
        )

    def get_futures_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures order-book depth."""
        return self._request(
            "GET",
            FuturesMarket.DEPTH,
            {"symbol": self._symbol(product_symbol), "limit": limit},
            signed=False,
        )

    def get_spot_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent Aster spot trades."""
        return self._request(
            "GET",
            SpotMarket.TRADES,
            {"symbol": self._symbol(product_symbol), "limit": limit},
            signed=False,
        )

    def get_futures_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent Aster futures trades."""
        return self._request(
            "GET",
            FuturesMarket.TRADES,
            {"symbol": self._symbol(product_symbol), "limit": limit},
            signed=False,
        )

    def get_spot_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        fromId: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve historical Aster spot trades."""
        return self._request(
            "GET",
            SpotMarket.HISTORICAL_TRADES,
            {"symbol": self._symbol(product_symbol), "limit": limit, "fromId": fromId},
            signed=False,
        )

    def get_futures_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        fromId: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve historical Aster futures trades."""
        return self._request(
            "GET",
            FuturesMarket.HISTORICAL_TRADES,
            {"symbol": self._symbol(product_symbol), "limit": limit, "fromId": fromId},
            signed=False,
        )

    def get_spot_agg_trades(
        self,
        product_symbol: str,
        fromId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve aggregate Aster spot trades."""
        return self._request(
            "GET",
            SpotMarket.AGG_TRADES,
            {
                "symbol": self._symbol(product_symbol),
                "fromId": fromId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
        )

    def get_futures_agg_trades(
        self,
        product_symbol: str,
        fromId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve aggregate Aster futures trades."""
        return self._request(
            "GET",
            FuturesMarket.AGG_TRADES,
            {
                "symbol": self._symbol(product_symbol),
                "fromId": fromId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
        )

    def get_spot_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot candlesticks."""
        return self._request(
            "GET",
            SpotMarket.KLINES,
            {
                "symbol": self._symbol(product_symbol),
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
        )

    def get_futures_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures candlesticks."""
        return self._request(
            "GET",
            FuturesMarket.KLINES,
            {
                "symbol": self._symbol(product_symbol),
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
        )

    def get_futures_index_price_klines(
        self,
        pair: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures index-price candlesticks."""
        return self._request(
            "GET",
            FuturesMarket.INDEX_PRICE_KLINES,
            {
                "pair": pair,
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
        )

    def get_futures_mark_price_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures mark-price candlesticks."""
        return self._request(
            "GET",
            FuturesMarket.MARK_PRICE_KLINES,
            {
                "symbol": self._symbol(product_symbol),
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
        )

    def get_spot_ticker_24hr(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot 24-hour ticker data."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request("GET", SpotMarket.TICKER_24HR, {"symbol": symbol}, signed=False)

    def get_futures_ticker_24hr(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures 24-hour ticker data."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request("GET", FuturesMarket.TICKER_24HR, {"symbol": symbol}, signed=False)

    def get_spot_ticker_price(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve latest Aster spot prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request("GET", SpotMarket.TICKER_PRICE, {"symbol": symbol}, signed=False)

    def get_futures_ticker_price(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve latest Aster futures prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request("GET", FuturesMarket.TICKER_PRICE, {"symbol": symbol}, signed=False)

    def get_spot_book_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot best bid and ask prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request("GET", SpotMarket.BOOK_TICKER, {"symbol": symbol}, signed=False)

    def get_futures_book_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures best bid and ask prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request("GET", FuturesMarket.BOOK_TICKER, {"symbol": symbol}, signed=False)

    def get_spot_commission_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve signed Aster spot commission rates."""
        return self._request(
            "GET",
            SpotMarket.COMMISSION_RATE,
            {"symbol": self._symbol(product_symbol)},
        )

    def get_spot_withdraw_fee(
        self,
        chainId: str,
        asset: str,
    ) -> dict[str, Any] | list[Any]:
        """Estimate the public Aster withdrawal fee without creating a withdrawal."""
        return self._request(
            "GET",
            SpotMarket.WITHDRAW_FEE,
            {"chainId": chainId, "asset": asset},
            signed=False,
        )

    def get_futures_premium_index(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures mark and index prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request("GET", FuturesMarket.PREMIUM_INDEX, {"symbol": symbol}, signed=False)

    def get_futures_funding_rate(
        self,
        product_symbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures funding-rate history."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request(
            "GET",
            FuturesMarket.FUNDING_RATE,
            {
                "symbol": symbol,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
        )

    def get_futures_funding_info(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures funding-rate configuration."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return self._request("GET", FuturesMarket.FUNDING_INFO, {"symbol": symbol}, signed=False)

    def get_futures_index_references(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures index reference components."""
        return self._request(
            "GET",
            FuturesMarket.INDEX_REFERENCES,
            {"symbol": self._symbol(product_symbol)},
            signed=False,
        )
