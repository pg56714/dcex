"""Backpack public market-data HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import Public


class MarketHTTP(HTTPManager):
    """HTTP client for Backpack public REST APIs."""

    def _symbol(self, product_symbol: str) -> str:
        if "_" in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.BACKPACK, product_symbol)

    def get_assets(self, country: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack asset metadata."""
        return self._request("GET", Public.ASSETS, {"country": country}, signed=False)

    def get_collateral(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public collateral parameters."""
        return self._request("GET", Public.COLLATERAL, signed=False)

    def get_borrow_lend_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend markets."""
        return self._request("GET", Public.BORROW_LEND_MARKETS, signed=False)

    def get_borrow_lend_market_history(
        self,
        interval: str,
        symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend market history."""
        return self._request(
            "GET",
            Public.BORROW_LEND_MARKET_HISTORY,
            {"interval": interval, "symbol": symbol},
            signed=False,
        )

    def get_borrow_lend_apy(self, tierId: int | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend APY rates."""
        return self._request("GET", Public.BORROW_LEND_APY, {"tierId": tierId}, signed=False)

    def get_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack markets."""
        return self._request("GET", Public.MARKETS, signed=False)

    def get_market(self, product_symbol: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack market."""
        return self._request(
            "GET",
            Public.MARKET,
            {"symbol": self._symbol(product_symbol)},
            signed=False,
        )

    def get_order_book_depth(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack order book depth."""
        return self._request(
            "GET",
            Public.DEPTH,
            {"symbol": self._symbol(product_symbol), "limit": limit},
            signed=False,
        )

    def get_market_sessions(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack market sessions."""
        return self._request("GET", Public.MARKET_SESSIONS, signed=False)

    def get_securities(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack securities."""
        return self._request("GET", Public.SECURITIES, signed=False)

    def get_mark_prices(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack mark prices."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return self._request(
            "GET",
            Public.MARK_PRICES,
            {"symbol": symbol, "marketType": marketType},
            signed=False,
        )

    def get_open_interest(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open interest."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return self._request("GET", Public.OPEN_INTEREST, {"symbol": symbol}, signed=False)

    def get_funding_rates(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical funding rates."""
        return self._request(
            "GET",
            Public.FUNDING_RATES,
            {"symbol": self._symbol(product_symbol), "limit": limit, "offset": offset},
            signed=False,
        )

    def get_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int,
        endTime: int | None = None,
        priceType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack candlesticks."""
        return self._request(
            "GET",
            Public.KLINES,
            {
                "symbol": self._symbol(product_symbol),
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "priceType": priceType,
            },
            signed=False,
        )

    def get_ticker(
        self,
        product_symbol: str,
        interval: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack ticker."""
        return self._request(
            "GET",
            Public.TICKER,
            {"symbol": self._symbol(product_symbol), "interval": interval},
            signed=False,
        )

    def get_tickers(self, interval: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack tickers."""
        return self._request("GET", Public.TICKERS, {"interval": interval}, signed=False)

    def get_status(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system status."""
        return self._request("GET", Public.STATUS, signed=False)

    def ping(self) -> dict[str, Any] | list[Any] | str:
        """Ping Backpack REST API."""
        return self._request("GET", Public.PING, signed=False)

    def get_time(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system time."""
        return self._request("GET", Public.TIME, signed=False)

    def get_wallets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public wallet addresses."""
        return self._request("GET", Public.WALLETS, signed=False)

    def get_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack recent public trades."""
        return self._request(
            "GET",
            Public.TRADES,
            {"symbol": self._symbol(product_symbol), "limit": limit},
            signed=False,
        )

    def get_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical public trades."""
        return self._request(
            "GET",
            Public.HISTORICAL_TRADES,
            {"symbol": self._symbol(product_symbol), "limit": limit, "offset": offset},
            signed=False,
        )
