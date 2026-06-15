"""Binance async public market API wrappers backed by Rust."""

from typing import Any

from ..._native_http import NativeResponse
from ._http_manager import HTTPManager
from .enums import BinanceProductType


class MarketHTTP(HTTPManager):
    """Async HTTP client for Binance market data API endpoints."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Binance public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Binance native client is required for public market methods.")
        status, headers, body = await self._native_client.public_request_async(method_name, params)
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, list):
                params.extend((key, str(item)) for item in value)
            else:
                params.append((key, str(value)))
        return params

    async def get_server_time(self, market_type: str = BinanceProductType.SPOT) -> dict:
        """Get Binance server time for spot or futures."""
        return await self._native_public(
            "get_server_time",
            self._params(market_type=str(market_type)),
        )

    async def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        product_symbols: list[str] | None = None,
        symbolStatus: str | None = None,
    ) -> dict:
        """Get spot exchange information."""
        return await self._native_public(
            "get_spot_exchange_info",
            self._params(
                product_symbol=product_symbol,
                product_symbols=product_symbols,
                symbolStatus=symbolStatus,
            ),
        )

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get spot order book data."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def get_spot_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get recent spot trades."""
        return await self._native_public(
            "get_spot_trades",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def get_spot_price(
        self,
        product_symbol: str | None = None,
        product_symbols: list[str] | None = None,
        symbolStatus: str | None = None,
    ) -> dict:
        """Get spot price information."""
        return await self._native_public(
            "get_spot_price",
            self._params(
                product_symbol=product_symbol,
                product_symbols=product_symbols,
                symbolStatus=symbolStatus,
            ),
        )

    async def get_klines(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get kline/candlestick data."""
        return await self._native_public(
            "get_klines",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                limit=limit,
            ),
        )

    async def get_futures_exchange_info(self) -> dict:
        """Get futures exchange information."""
        return await self._native_public("get_futures_exchange_info", [])

    async def get_futures_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get futures ticker information."""
        return await self._native_public(
            "get_futures_ticker",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_premium_index(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get futures premium index."""
        return await self._native_public(
            "get_futures_premium_index",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_funding_rate(
        self,
        product_symbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get futures funding rate history."""
        return await self._native_public(
            "get_futures_funding_rate",
            self._params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_futures_open_interest(self, product_symbol: str) -> dict:
        """Get current futures open interest."""
        return await self._native_public(
            "get_futures_open_interest",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_open_interest_history(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict:
        """Get futures open interest statistics history."""
        return await self._native_public(
            "get_futures_open_interest_history",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_futures_global_long_short_account_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict:
        """Get global futures long/short account ratio history."""
        return await self._native_public(
            "get_futures_global_long_short_account_ratio",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_futures_top_long_short_account_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict:
        """Get top trader futures long/short account ratio history."""
        return await self._native_public(
            "get_futures_top_long_short_account_ratio",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_futures_top_long_short_position_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict:
        """Get top trader futures long/short position ratio history."""
        return await self._native_public(
            "get_futures_top_long_short_position_ratio",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_futures_taker_buy_sell_volume(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict:
        """Get futures taker buy/sell volume history."""
        return await self._native_public(
            "get_futures_taker_buy_sell_volume",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_futures_basis(
        self,
        product_symbol: str,
        contractType: str = "PERPETUAL",
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict:
        """Get futures basis history."""
        return await self._native_public(
            "get_futures_basis",
            self._params(
                product_symbol=product_symbol,
                contractType=contractType,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )
