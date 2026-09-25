"""Binance async public market API wrappers backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager
from .enums import BinanceProductType


class MarketHTTP(HTTPManager):
    """Async HTTP client for Binance market data API endpoints."""

    async def get_equity_exchange_info(self, product_symbol: str | None = None) -> dict:
        """Get stock symbols and their order-size rules (requires an API key)."""
        return await self._native_public(
            "get_equity_exchange_info", self._params(product_symbol=product_symbol)
        )

    async def get_equity_tokenized_assets(self) -> list[dict]:
        """Get stock tokens available for conversion (requires an API key)."""
        return await self._native_public("get_equity_tokenized_assets", [])

    async def get_equity_quote(self, product_symbol: str) -> dict:
        """Get the latest bid and ask for a stock symbol."""
        return await self._native_public(
            "get_equity_quote", self._params(product_symbol=product_symbol)
        )

    async def get_options_exchange_info(self) -> dict[str, Any]:
        """Get Binance Options contracts and trading rules."""
        return await self._native_public("get_options_exchange_info", [])

    async def get_options_exercise_history(
        self,
        underlying: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get historical option exercise records."""
        return await self._native_public(
            "get_options_exercise_history",
            self._params(
                underlying=underlying,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_options_index_price(self, underlying: str) -> dict[str, Any]:
        """Get the spot index price for an option underlying."""
        return await self._native_public(
            "get_options_index_price", self._params(underlying=underlying)
        )

    async def get_options_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        """Get candlesticks for an option symbol."""
        return await self._native_public(
            "get_options_klines",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_options_open_interest(
        self, underlyingAsset: str, expiration: str
    ) -> list[dict[str, Any]]:
        """Get option open interest by underlying asset and expiration."""
        return await self._native_public(
            "get_options_open_interest",
            self._params(underlyingAsset=underlyingAsset, expiration=expiration),
        )

    async def get_options_mark_price(
        self, product_symbol: str | None = None
    ) -> list[dict[str, Any]]:
        """Get option mark prices and Greeks."""
        return await self._native_public(
            "get_options_mark_price", self._params(product_symbol=product_symbol)
        )

    async def get_options_orderbook(
        self, product_symbol: str, limit: int | None = None
    ) -> dict[str, Any]:
        """Get an option order book."""
        return await self._native_public(
            "get_options_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def get_options_block_trades(self) -> list[dict[str, Any]]:
        """Get recent public option block trades."""
        return await self._native_public("get_options_block_trades", [])

    async def get_options_trades(
        self, product_symbol: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get recent option trades."""
        return await self._native_public(
            "get_options_trades",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def ping_options(self) -> dict[str, Any]:
        """Test Binance Options REST connectivity."""
        return await self._native_public("ping_options", [])

    async def get_options_ticker(self, product_symbol: str | None = None) -> list[dict[str, Any]]:
        """Get 24-hour option ticker statistics."""
        return await self._native_public(
            "get_options_ticker", self._params(product_symbol=product_symbol)
        )

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Binance public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Binance native client is required for public market methods.")
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
            if isinstance(value, list):
                params.extend((key, str(item)) for item in value)
            else:
                if isinstance(value, bool):
                    value = str(value).lower()
                params.append((key, str(value)))
        return params

    async def get_server_time(self, market_type: str = BinanceProductType.SPOT) -> dict:
        """Get Binance server time for spot, futures, equity, or options."""
        return await self._native_public(
            "get_server_time",
            self._params(market_type=str(market_type)),
        )

    async def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        product_symbols: list[str] | None = None,
        permissions: list[str] | None = None,
        showPermissionSets: bool | None = None,
        symbolStatus: str | None = None,
    ) -> dict:
        """Get spot exchange information."""
        return await self._native_public(
            "get_spot_exchange_info",
            self._params(
                product_symbol=product_symbol,
                product_symbols=product_symbols,
                permissions=permissions,
                showPermissionSets=showPermissionSets,
                symbolStatus=symbolStatus,
            ),
        )

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
        symbolStatus: str | None = None,
    ) -> dict:
        """Get spot order book data."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(
                product_symbol=product_symbol,
                limit=limit,
                symbolStatus=symbolStatus,
            ),
        )

    async def get_spot_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        symbolStatus: str | None = None,
    ) -> dict:
        """Get recent spot trades."""
        return await self._native_public(
            "get_spot_trades",
            self._params(
                product_symbol=product_symbol,
                limit=limit,
                symbolStatus=symbolStatus,
            ),
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
        end_time: int | None = None,
        time_zone: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get kline/candlestick data."""
        return await self._native_public(
            "get_klines",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                time_zone=time_zone,
                limit=limit,
            ),
        )

    async def get_futures_exchange_info(self) -> dict:
        """Get futures exchange information."""
        return await self._native_public("get_futures_exchange_info", [])

    async def get_futures_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get USDⓈ-M futures order book data."""
        return await self._native_public(
            "get_futures_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

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
