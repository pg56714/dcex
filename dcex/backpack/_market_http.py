"""Backpack public market-data HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for Backpack public REST APIs."""

    def _symbol(self, product_symbol: str) -> str:
        if "_" in product_symbol:
            return product_symbol
        if hasattr(self, "ptm"):
            return self.ptm.get_exchange_symbol(Common.BACKPACK, product_symbol)
        parts = product_symbol.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}_{parts[1]}" if parts[2] == "SPOT" else f"{parts[0]}_{parts[1]}_PERP"
        return product_symbol

    def get_assets(self, country: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack asset metadata."""
        return self._native_public("get_assets", self._native_params(country=country))

    def get_collateral(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public collateral parameters."""
        return self._native_public("get_collateral", [])

    def get_borrow_lend_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend markets."""
        return self._native_public("get_borrow_lend_markets", [])

    def get_borrow_lend_market_history(
        self,
        interval: str,
        symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend market history."""
        return self._native_public(
            "get_borrow_lend_market_history",
            self._native_params(interval=interval, symbol=symbol),
        )

    def get_borrow_lend_apy(self, tierId: int | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend APY rates."""
        return self._native_public("get_borrow_lend_apy", self._native_params(tierId=tierId))

    def get_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack markets."""
        return self._native_public("get_markets", [])

    def get_market(self, product_symbol: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack market."""
        return self._native_public(
            "get_market",
            self._native_params(product_symbol=product_symbol),
        )

    def get_order_book_depth(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack order book depth."""
        return self._native_public(
            "get_order_book_depth",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_market_sessions(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack market sessions."""
        return self._native_public("get_market_sessions", [])

    def get_securities(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack securities."""
        return self._native_public("get_securities", [])

    def get_mark_prices(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack mark prices."""
        return self._native_public(
            "get_mark_prices",
            self._native_params(product_symbol=product_symbol, marketType=marketType),
        )

    def get_open_interest(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open interest."""
        return self._native_public(
            "get_open_interest",
            self._native_params(product_symbol=product_symbol),
        )

    def get_funding_rates(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical funding rates."""
        return self._native_public(
            "get_funding_rates",
            self._native_params(product_symbol=product_symbol, limit=limit, offset=offset),
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
        return self._native_public(
            "get_klines",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                priceType=priceType,
            ),
        )

    def get_ticker(
        self,
        product_symbol: str,
        interval: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack ticker."""
        return self._native_public(
            "get_ticker",
            self._native_params(product_symbol=product_symbol, interval=interval),
        )

    def get_tickers(self, interval: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack tickers."""
        return self._native_public("get_tickers", self._native_params(interval=interval))

    def get_status(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system status."""
        return self._native_public("get_status", [])

    def ping(self) -> dict[str, Any] | list[Any] | str:
        """Ping Backpack REST API."""
        return self._native_public("ping", [])

    def get_time(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system time."""
        return self._native_public("get_time", [])

    def get_wallets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public wallet addresses."""
        return self._native_public("get_wallets", [])

    def get_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack recent public trades."""
        return self._native_public(
            "get_recent_trades",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical public trades."""
        return self._native_public(
            "get_historical_trades",
            self._native_params(product_symbol=product_symbol, limit=limit, offset=offset),
        )
