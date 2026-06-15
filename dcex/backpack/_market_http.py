"""Backpack public market-data HTTP client."""

from typing import Any

from .._native_http import NativeResponse
from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import Public


class MarketHTTP(HTTPManager):
    """HTTP client for Backpack public REST APIs."""

    def _native_public(
        self,
        path: str,
        params: list[tuple[str, str]] | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Call a Rust-backed Backpack public endpoint and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Backpack native client is required for public market methods.")
        status, headers, body = self._native_client.public_request(path, params or [])
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            params.append((key, str(value)))
        return params

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
        return self._native_public(Public.ASSETS, self._params(country=country))

    def get_collateral(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public collateral parameters."""
        return self._native_public(Public.COLLATERAL)

    def get_borrow_lend_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend markets."""
        return self._native_public(Public.BORROW_LEND_MARKETS)

    def get_borrow_lend_market_history(
        self,
        interval: str,
        symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend market history."""
        return self._native_public(
            Public.BORROW_LEND_MARKET_HISTORY,
            self._params(interval=interval, symbol=symbol),
        )

    def get_borrow_lend_apy(self, tierId: int | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend APY rates."""
        return self._native_public(Public.BORROW_LEND_APY, self._params(tierId=tierId))

    def get_markets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack markets."""
        return self._native_public(Public.MARKETS)

    def get_market(self, product_symbol: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack market."""
        return self._native_public(
            Public.MARKET,
            self._params(symbol=self._symbol(product_symbol)),
        )

    def get_order_book_depth(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack order book depth."""
        return self._native_public(
            Public.DEPTH,
            self._params(symbol=self._symbol(product_symbol), limit=limit),
        )

    def get_market_sessions(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack market sessions."""
        return self._native_public(Public.MARKET_SESSIONS)

    def get_securities(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack securities."""
        return self._native_public(Public.SECURITIES)

    def get_mark_prices(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack mark prices."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return self._native_public(
            Public.MARK_PRICES,
            self._params(symbol=symbol, marketType=marketType),
        )

    def get_open_interest(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open interest."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return self._native_public(Public.OPEN_INTEREST, self._params(symbol=symbol))

    def get_funding_rates(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical funding rates."""
        return self._native_public(
            Public.FUNDING_RATES,
            self._params(symbol=self._symbol(product_symbol), limit=limit, offset=offset),
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
            Public.KLINES,
            self._params(
                symbol=self._symbol(product_symbol),
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
            Public.TICKER,
            self._params(symbol=self._symbol(product_symbol), interval=interval),
        )

    def get_tickers(self, interval: str | None = None) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack tickers."""
        return self._native_public(Public.TICKERS, self._params(interval=interval))

    def get_status(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system status."""
        return self._native_public(Public.STATUS)

    def ping(self) -> dict[str, Any] | list[Any] | str:
        """Ping Backpack REST API."""
        return self._native_public(Public.PING)

    def get_time(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack system time."""
        return self._native_public(Public.TIME)

    def get_wallets(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack public wallet addresses."""
        return self._native_public(Public.WALLETS)

    def get_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack recent public trades."""
        return self._native_public(
            Public.TRADES,
            self._params(symbol=self._symbol(product_symbol), limit=limit),
        )

    def get_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack historical public trades."""
        return self._native_public(
            Public.HISTORICAL_TRADES,
            self._params(symbol=self._symbol(product_symbol), limit=limit, offset=offset),
        )
