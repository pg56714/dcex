"""Backpack public market-data async HTTP client."""

from collections.abc import Mapping
from typing import Any, Literal

from ..._native_http import NativeResponse
from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import Public


class MarketHTTP(HTTPManager):
    """Async HTTP client for Backpack public REST APIs."""

    @staticmethod
    def _native_params(query: dict[str, Any] | None) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []
        for key, value in (query or {}).items():
            if value is None:
                continue
            if isinstance(value, bool):
                value = str(value).lower()
            params.append((key, str(value)))
        return params

    async def _request(
        self,
        method: Literal["GET", "POST", "PATCH", "DELETE"],
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = False,
        instruction: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        if (
            method.upper() == "GET"
            and not signed
            and instruction is None
            and headers is None
            and self._native_client is not None
        ):
            (
                status,
                response_headers,
                response_body,
            ) = await self._native_client.public_request_async(
                str(path),
                self._native_params(query),
            )
            response = NativeResponse(status, dict(response_headers), bytes(response_body))
            self._store_response_headers(response)
            return response.json()
        return await super()._request(method, path, query, signed, instruction, headers)

    def _symbol(self, product_symbol: str) -> str:
        if "_" in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.BACKPACK, product_symbol)

    async def get_assets(self, country: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack asset metadata."""
        return await self._request("GET", Public.ASSETS, {"country": country}, signed=False)

    async def get_collateral(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public collateral parameters."""
        return await self._request("GET", Public.COLLATERAL, signed=False)

    async def get_borrow_lend_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend markets."""
        return await self._request("GET", Public.BORROW_LEND_MARKETS, signed=False)

    async def get_borrow_lend_market_history(
        self,
        interval: str,
        symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend market history."""
        return await self._request(
            "GET",
            Public.BORROW_LEND_MARKET_HISTORY,
            {"interval": interval, "symbol": symbol},
            signed=False,
        )

    async def get_borrow_lend_apy(
        self,
        tierId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend APY rates."""
        return await self._request("GET", Public.BORROW_LEND_APY, {"tierId": tierId}, signed=False)

    async def get_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack markets."""
        return await self._request("GET", Public.MARKETS, signed=False)

    async def get_market(self, product_symbol: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack market."""
        return await self._request(
            "GET",
            Public.MARKET,
            {"symbol": self._symbol(product_symbol)},
            signed=False,
        )

    async def get_order_book_depth(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack order book depth."""
        return await self._request(
            "GET",
            Public.DEPTH,
            {"symbol": self._symbol(product_symbol), "limit": limit},
            signed=False,
        )

    async def get_market_sessions(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack market sessions."""
        return await self._request("GET", Public.MARKET_SESSIONS, signed=False)

    async def get_securities(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack securities."""
        return await self._request("GET", Public.SECURITIES, signed=False)

    async def get_mark_prices(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack mark prices."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            Public.MARK_PRICES,
            {"symbol": symbol, "marketType": marketType},
            signed=False,
        )

    async def get_open_interest(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open interest."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request("GET", Public.OPEN_INTEREST, {"symbol": symbol}, signed=False)

    async def get_funding_rates(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical funding rates."""
        return await self._request(
            "GET",
            Public.FUNDING_RATES,
            {"symbol": self._symbol(product_symbol), "limit": limit, "offset": offset},
            signed=False,
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
        return await self._request(
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

    async def get_ticker(
        self,
        product_symbol: str,
        interval: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack ticker."""
        return await self._request(
            "GET",
            Public.TICKER,
            {"symbol": self._symbol(product_symbol), "interval": interval},
            signed=False,
        )

    async def get_tickers(self, interval: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack tickers."""
        return await self._request("GET", Public.TICKERS, {"interval": interval}, signed=False)

    async def get_status(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system status."""
        return await self._request("GET", Public.STATUS, signed=False)

    async def ping(self) -> dict[str, Any] | list[Any] | str:
        """Ping Backpack REST API."""
        return await self._request("GET", Public.PING, signed=False)

    async def get_time(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system time."""
        return await self._request("GET", Public.TIME, signed=False)

    async def get_wallets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public wallet addresses."""
        return await self._request("GET", Public.WALLETS, signed=False)

    async def get_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack recent public trades."""
        return await self._request(
            "GET",
            Public.TRADES,
            {"symbol": self._symbol(product_symbol), "limit": limit},
            signed=False,
        )

    async def get_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical public trades."""
        return await self._request(
            "GET",
            Public.HISTORICAL_TRADES,
            {"symbol": self._symbol(product_symbol), "limit": limit, "offset": offset},
            signed=False,
        )
