"""Binance public market API wrappers backed by Rust."""

from typing import Any

from .._native_http import request_native_json
from ._http_manager import HTTPManager
from .enums import BinanceProductType


class MarketHTTP(HTTPManager):
    """HTTP client for Binance market data API endpoints."""

    def get_equity_exchange_info(self, product_symbol: str | None = None) -> dict:
        """Get stock symbols and their order-size rules (requires an API key)."""
        return self._native_public(
            "get_equity_exchange_info", self._params(product_symbol=product_symbol)
        )

    def get_equity_tokenized_assets(self) -> list[dict]:
        """Get stock tokens available for conversion (requires an API key)."""
        return self._native_public("get_equity_tokenized_assets", [])

    def get_equity_quote(self, product_symbol: str) -> dict:
        """Get the latest bid and ask for a stock symbol."""
        return self._native_public("get_equity_quote", self._params(product_symbol=product_symbol))

    def get_options_exchange_info(self) -> dict[str, Any]:
        """Get Binance Options contracts and trading rules."""
        return self._native_public("get_options_exchange_info", [])

    def get_options_exercise_history(
        self,
        underlying: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get historical option exercise records."""
        return self._native_public(
            "get_options_exercise_history",
            self._params(
                underlying=underlying,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_options_index_price(self, underlying: str) -> dict[str, Any]:
        """Get the spot index price for an option underlying."""
        return self._native_public("get_options_index_price", self._params(underlying=underlying))

    def get_options_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        """Get candlesticks for an option symbol."""
        return self._native_public(
            "get_options_klines",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_options_open_interest(
        self, underlyingAsset: str, expiration: str
    ) -> list[dict[str, Any]]:
        """Get option open interest by underlying asset and expiration."""
        return self._native_public(
            "get_options_open_interest",
            self._params(underlyingAsset=underlyingAsset, expiration=expiration),
        )

    def get_options_mark_price(self, product_symbol: str | None = None) -> list[dict[str, Any]]:
        """Get option mark prices and Greeks."""
        return self._native_public(
            "get_options_mark_price", self._params(product_symbol=product_symbol)
        )

    def get_options_orderbook(
        self, product_symbol: str, limit: int | None = None
    ) -> dict[str, Any]:
        """Get an option order book."""
        return self._native_public(
            "get_options_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    def get_options_block_trades(self) -> list[dict[str, Any]]:
        """Get recent public option block trades."""
        return self._native_public("get_options_block_trades", [])

    def get_options_trades(
        self, product_symbol: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get recent option trades."""
        return self._native_public(
            "get_options_trades",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    def ping_options(self) -> dict[str, Any]:
        """Test Binance Options REST connectivity."""
        return self._native_public("ping_options", [])

    def get_options_ticker(self, product_symbol: str | None = None) -> list[dict[str, Any]]:
        """Get 24-hour option ticker statistics."""
        return self._native_public(
            "get_options_ticker", self._params(product_symbol=product_symbol)
        )

    def _native_public(self, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        """Call a Rust-backed Binance public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Binance native client is required for public market methods.")
        response, data = request_native_json(
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

    def get_server_time(self, market_type: str = BinanceProductType.SPOT) -> dict[str, Any]:
        """Get Binance server time for spot, futures, equity, or options."""
        return self._native_public(
            "get_server_time",
            self._params(market_type=str(market_type)),
        )

    def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        product_symbols: list[str] | None = None,
        permissions: list[str] | None = None,
        showPermissionSets: bool | None = None,
        symbolStatus: str | None = None,
    ) -> dict[str, Any]:
        """Get spot trading exchange information from Binance."""
        return self._native_public(
            "get_spot_exchange_info",
            self._params(
                product_symbol=product_symbol,
                product_symbols=product_symbols,
                permissions=permissions,
                showPermissionSets=showPermissionSets,
                symbolStatus=symbolStatus,
            ),
        )

    def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
        symbolStatus: str | None = None,
    ) -> dict[str, Any]:
        """Get spot order book data from Binance."""
        return self._native_public(
            "get_spot_orderbook",
            self._params(
                product_symbol=product_symbol,
                limit=limit,
                symbolStatus=symbolStatus,
            ),
        )

    def get_spot_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        symbolStatus: str | None = None,
    ) -> dict[str, Any]:
        """Get recent spot trades from Binance."""
        return self._native_public(
            "get_spot_trades",
            self._params(
                product_symbol=product_symbol,
                limit=limit,
                symbolStatus=symbolStatus,
            ),
        )

    def get_spot_price(
        self,
        product_symbol: str | None = None,
        product_symbols: list[str] | None = None,
        symbolStatus: str | None = None,
    ) -> dict[str, Any]:
        """Get latest spot price for a symbol, symbols, or all symbols."""
        return self._native_public(
            "get_spot_price",
            self._params(
                product_symbol=product_symbol,
                product_symbols=product_symbols,
                symbolStatus=symbolStatus,
            ),
        )

    def get_klines(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get kline/candlestick data from Binance."""
        return self._native_public(
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

    def get_futures_exchange_info(self) -> dict[str, Any]:
        """Get futures trading exchange information from Binance."""
        return self._native_public("get_futures_exchange_info", [])

    def get_futures_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get futures ticker data from Binance."""
        return self._native_public(
            "get_futures_ticker",
            self._params(product_symbol=product_symbol),
        )

    def get_futures_premium_index(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get futures premium index data from Binance."""
        return self._native_public(
            "get_futures_premium_index",
            self._params(product_symbol=product_symbol),
        )

    def get_futures_funding_rate(
        self,
        product_symbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get futures funding rate history from Binance."""
        return self._native_public(
            "get_futures_funding_rate",
            self._params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_futures_open_interest(self, product_symbol: str) -> dict[str, Any]:
        """Get current futures open interest for a symbol."""
        return self._native_public(
            "get_futures_open_interest",
            self._params(product_symbol=product_symbol),
        )

    def get_futures_open_interest_history(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get futures open interest statistics history."""
        return self._native_public(
            "get_futures_open_interest_history",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_futures_global_long_short_account_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get global futures long/short account ratio history."""
        return self._native_public(
            "get_futures_global_long_short_account_ratio",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_futures_top_long_short_account_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get top trader futures long/short account ratio history."""
        return self._native_public(
            "get_futures_top_long_short_account_ratio",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_futures_top_long_short_position_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get top trader futures long/short position ratio history."""
        return self._native_public(
            "get_futures_top_long_short_position_ratio",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_futures_taker_buy_sell_volume(
        self,
        product_symbol: str,
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get futures taker buy/sell volume history."""
        return self._native_public(
            "get_futures_taker_buy_sell_volume",
            self._params(
                product_symbol=product_symbol,
                period=period,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_futures_basis(
        self,
        product_symbol: str,
        contractType: str = "PERPETUAL",
        period: str = "5m",
        limit: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get futures basis history."""
        return self._native_public(
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
