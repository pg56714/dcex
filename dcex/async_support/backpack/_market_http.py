"""Backpack public market-data async HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for Backpack public REST APIs."""

    def _symbol(self, product_symbol: str) -> str:
        if "_" in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.BACKPACK, product_symbol)

    async def get_assets(self, country: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack asset metadata."""
        return await self._native_public("get_assets", self._native_params(country=country))

    async def get_collateral(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public collateral parameters."""
        return await self._native_public("get_collateral", [])

    async def get_borrow_lend_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend markets."""
        return await self._native_public("get_borrow_lend_markets", [])

    async def get_borrow_lend_market_history(
        self,
        interval: str,
        symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend market history."""
        return await self._native_public(
            "get_borrow_lend_market_history",
            self._native_params(interval=interval, symbol=symbol),
        )

    async def get_borrow_lend_apy(
        self,
        tierId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend APY rates."""
        return await self._native_public(
            "get_borrow_lend_apy",
            self._native_params(tierId=tierId),
        )

    async def get_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack markets."""
        return await self._native_public("get_markets", [])

    async def get_market(self, product_symbol: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack market."""
        return await self._native_public(
            "get_market",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_order_book_depth(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack order book depth."""
        return await self._native_public(
            "get_order_book_depth",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    async def get_market_sessions(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack market sessions."""
        return await self._native_public("get_market_sessions", [])

    async def get_securities(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack securities."""
        return await self._native_public("get_securities", [])

    async def get_mark_prices(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack mark prices."""
        return await self._native_public(
            "get_mark_prices",
            self._native_params(product_symbol=product_symbol, marketType=marketType),
        )

    async def get_open_interest(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open interest."""
        return await self._native_public(
            "get_open_interest",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_funding_rates(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical funding rates."""
        return await self._native_public(
            "get_funding_rates",
            self._native_params(product_symbol=product_symbol, limit=limit, offset=offset),
        )

    async def get_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int,
        endTime: int | None = None,
        priceType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack candlesticks."""
        return await self._native_public(
            "get_klines",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                priceType=priceType,
            ),
        )

    async def get_ticker(
        self,
        product_symbol: str,
        interval: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack ticker."""
        return await self._native_public(
            "get_ticker",
            self._native_params(product_symbol=product_symbol, interval=interval),
        )

    async def get_tickers(self, interval: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack tickers."""
        return await self._native_public("get_tickers", self._native_params(interval=interval))

    async def get_status(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system status."""
        return await self._native_public("get_status", [])

    async def ping(self) -> dict[str, Any] | list[Any] | str:
        """Ping Backpack REST API."""
        return await self._native_public("ping", [])

    async def get_time(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system time."""
        return await self._native_public("get_time", [])

    async def get_wallets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public wallet addresses."""
        return await self._native_public("get_wallets", [])

    async def get_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack recent public trades."""
        return await self._native_public(
            "get_recent_trades",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    async def get_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical public trades."""
        return await self._native_public(
            "get_historical_trades",
            self._native_params(product_symbol=product_symbol, limit=limit, offset=offset),
        )
