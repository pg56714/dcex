"""KuCoin Spot and Futures Market async HTTP client backed by Rust."""

import json
from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for KuCoin public market API operations."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed KuCoin public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("KuCoin native client is required for public market methods.")
        response, data = await request_native_json_async(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            if key == "from_":
                key = "from"
            if isinstance(value, list):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

    async def get_spot_instrument_info(self, market: str | None = None) -> dict[str, Any]:
        """Retrieve trading instrument information."""
        return await self._native_public(
            "get_spot_instrument_info",
            self._params(market=market),
        )

    async def get_spot_ticker(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve single ticker information for a specific trading pair."""
        return await self._native_public(
            "get_spot_ticker",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_all_tickers(self) -> dict[str, Any]:
        """Retrieve ticker information for all trading pairs."""
        return await self._native_public("get_spot_all_tickers", [])

    async def get_spot_orderbook(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve orderbook data for a specific trading pair."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_public_trades(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve public trade history for a specific trading pair."""
        return await self._native_public(
            "get_spot_public_trades",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_kline(
        self,
        product_symbol: str,
        timeframe: str,
        startAt: int | None = None,
        endAt: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve candlestick/K-line data for a specific trading pair."""
        return await self._native_public(
            "get_spot_kline",
            self._params(
                product_symbol=product_symbol,
                timeframe=timeframe,
                startAt=startAt,
                endAt=endAt,
            ),
        )

    async def get_futures_contracts(self) -> dict[str, Any]:
        """Retrieve active KuCoin futures contracts."""
        return await self._native_public("get_futures_contracts", [])

    async def get_futures_contract(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve one KuCoin futures contract."""
        return await self._native_public(
            "get_futures_contract",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_ticker(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve one KuCoin futures ticker."""
        return await self._native_public(
            "get_futures_ticker",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_orderbook(
        self,
        product_symbol: str | None = None,
        depth: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures orderbook."""
        return await self._native_public(
            "get_futures_orderbook",
            self._params(
                product_symbol=product_symbol,
                depth=depth,
            ),
        )

    async def get_futures_public_trades(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve KuCoin futures public trade history."""
        return await self._native_public(
            "get_futures_public_trades",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_kline(
        self,
        product_symbol: str,
        timeframe: str,
        from_: int | None = None,
        to: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures candlestick/K-line data."""
        return await self._native_public(
            "get_futures_kline",
            self._params(
                product_symbol=product_symbol,
                timeframe=timeframe,
                from_=from_,
                to=to,
            ),
        )

    async def get_futures_open_interest(
        self,
        product_symbol: str | list[str] | None = None,
        interval: str | None = None,
        startAt: int | None = None,
        endAt: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        """Get futures open interest history."""
        return await self._native_public(
            "get_futures_open_interest",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startAt=startAt,
                endAt=endAt,
                pageSize=pageSize,
            ),
        )

    async def get_uta_position_tiers(
        self,
        product_symbol: str | None = None,
        tradeType: str = "FUTURES",
        currency: str | None = None,
        marginMode: str = "CROSS",
        data: str = "RISK_LIMIT",
        accountType: str = "UNIFIED",
    ) -> dict[str, Any]:
        """Retrieve KuCoin UTA futures position tiers and risk limits."""
        return await self._native_public(
            "get_uta_position_tiers",
            self._params(
                product_symbol=product_symbol,
                tradeType=tradeType,
                currency=currency,
                marginMode=marginMode,
                data=data,
                accountType=accountType,
            ),
        )
