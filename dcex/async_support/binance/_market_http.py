# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
"""Binance async public market API wrappers backed by Rust."""

from json import dumps
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

    async def get_coin_futures_aggregate_trades(
        self,
        *,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /dapi/v1/aggTrades.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#compressed-aggregate-trades-list

        """
        return await self._native_public(
            "get_coin_futures_aggregate_trades",
            self._params(
                symbol=symbol, fromId=from_id, startTime=start_time, endTime=end_time, limit=limit
            ),
        )

    async def get_coin_futures_continuous_klines(
        self,
        *,
        pair: str,
        contract_type: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /dapi/v1/continuousKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#continuous-contract-kline-candlestick-data

        """
        return await self._native_public(
            "get_coin_futures_continuous_klines",
            self._params(
                pair=pair,
                contractType=contract_type,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_coin_futures_funding_info(self) -> Any:
        """

        GET /dapi/v1/fundingInfo.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#get-funding-rate-info

        """
        return await self._native_public("get_coin_futures_funding_info", self._params())

    async def get_coin_futures_index_price_klines(
        self,
        *,
        pair: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /dapi/v1/indexPriceKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#index-price-kline-candlestick-data

        """
        return await self._native_public(
            "get_coin_futures_index_price_klines",
            self._params(
                pair=pair, interval=interval, startTime=start_time, endTime=end_time, limit=limit
            ),
        )

    async def get_coin_futures_mark_price_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /dapi/v1/markPriceKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#mark-price-kline-candlestick-data

        """
        return await self._native_public(
            "get_coin_futures_mark_price_klines",
            self._params(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_coin_futures_open_interest(self, *, symbol: str) -> Any:
        """

        GET /dapi/v1/openInterest.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#open-interest

        """
        return await self._native_public(
            "get_coin_futures_open_interest", self._params(symbol=symbol)
        )

    async def get_coin_futures_premium_index_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /dapi/v1/premiumIndexKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#premium-index-kline-data

        """
        return await self._native_public(
            "get_coin_futures_premium_index_klines",
            self._params(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_coin_futures_book_ticker(
        self, *, symbol: str | None = None, pair: str | None = None
    ) -> Any:
        """

        GET /dapi/v1/ticker/bookTicker.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#symbol-order-book-ticker

        """
        return await self._native_public(
            "get_coin_futures_book_ticker", self._params(symbol=symbol, pair=pair)
        )

    async def get_coin_futures_24h_ticker(
        self, *, symbol: str | None = None, pair: str | None = None
    ) -> Any:
        """

        GET /dapi/v1/ticker/24hr.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#ticker24hr-price-change-statistics

        """
        return await self._native_public(
            "get_coin_futures_24h_ticker", self._params(symbol=symbol, pair=pair)
        )

    async def get_futures_aggregate_trades(
        self,
        *,
        product_symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /fapi/v1/aggTrades.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#compressed-aggregate-trades-list

        """
        return await self._native_public(
            "get_futures_aggregate_trades",
            self._params(
                product_symbol=product_symbol,
                fromId=from_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_futures_continuous_klines(
        self,
        *,
        pair: str,
        contract_type: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /fapi/v1/continuousKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#continuous-contract-kline-candlestick-data

        """
        return await self._native_public(
            "get_futures_continuous_klines",
            self._params(
                pair=pair,
                contractType=contract_type,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_futures_funding_info(self) -> Any:
        """

        GET /fapi/v1/fundingInfo.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#get-funding-rate-info

        """
        return await self._native_public("get_futures_funding_info", self._params())

    async def get_futures_index_price_klines(
        self,
        *,
        pair: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /fapi/v1/indexPriceKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#index-price-kline-candlestick-data

        """
        return await self._native_public(
            "get_futures_index_price_klines",
            self._params(
                pair=pair, interval=interval, startTime=start_time, endTime=end_time, limit=limit
            ),
        )

    async def get_futures_mark_price_klines(
        self,
        *,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /fapi/v1/markPriceKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#mark-price-kline-candlestick-data

        """
        return await self._native_public(
            "get_futures_mark_price_klines",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_futures_premium_index_klines(
        self,
        *,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /fapi/v1/premiumIndexKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#premium-index-kline-data

        """
        return await self._native_public(
            "get_futures_premium_index_klines",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_futures_recent_trades(
        self, *, product_symbol: str, limit: int | None = None
    ) -> Any:
        """

        GET /fapi/v1/trades.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#recent-trades-list

        """
        return await self._native_public(
            "get_futures_recent_trades", self._params(product_symbol=product_symbol, limit=limit)
        )

    async def get_futures_price_ticker_v1(self, *, product_symbol: str | None = None) -> Any:
        """

        GET /fapi/v1/ticker/price.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#symbol-price-ticker

        """
        return await self._native_public(
            "get_futures_price_ticker_v1", self._params(product_symbol=product_symbol)
        )

    async def get_futures_price_ticker(self, *, product_symbol: str | None = None) -> Any:
        """

        GET /fapi/v2/ticker/price.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#symbol-price-ticker-v2

        """
        return await self._native_public(
            "get_futures_price_ticker", self._params(product_symbol=product_symbol)
        )

    async def get_futures_24h_ticker(self, *, product_symbol: str | None = None) -> Any:
        """

        GET /fapi/v1/ticker/24hr.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#ticker24hr-price-change-statistics

        """
        return await self._native_public(
            "get_futures_24h_ticker", self._params(product_symbol=product_symbol)
        )

    async def get_margin_delist_schedule(self, *, recv_window: int | None = None) -> Any:
        """

        GET /sapi/v1/margin/delist-schedule.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-delist-schedule

        """
        return await self._native_public(
            "get_margin_delist_schedule", self._params(recvWindow=recv_window)
        )

    async def get_spot_aggregate_trades(
        self,
        *,
        product_symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        GET /api/v3/aggTrades.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#agg-trades

        """
        return await self._native_public(
            "get_spot_aggregate_trades",
            self._params(
                product_symbol=product_symbol,
                fromId=from_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_spot_average_price(self, *, product_symbol: str) -> Any:
        """

        GET /api/v3/avgPrice.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#avg-price

        """
        return await self._native_public(
            "get_spot_average_price", self._params(product_symbol=product_symbol)
        )

    async def get_spot_24h_ticker(
        self,
        *,
        product_symbol: str | None = None,
        symbols: list[str] | None = None,
        kind_type: str | None = None,
        symbol_status: str | None = None,
    ) -> Any:
        """

        GET /api/v3/ticker/24hr.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ticker24hr

        """
        return await self._native_public(
            "get_spot_24h_ticker",
            self._params(
                product_symbol=product_symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                type=kind_type,
                symbolStatus=symbol_status,
            ),
        )

    async def get_spot_book_ticker(
        self,
        *,
        product_symbol: str | None = None,
        symbols: list[str] | None = None,
        symbol_status: str | None = None,
    ) -> Any:
        """

        GET /api/v3/ticker/bookTicker.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ticker-book-ticker

        """
        return await self._native_public(
            "get_spot_book_ticker",
            self._params(
                product_symbol=product_symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                symbolStatus=symbol_status,
            ),
        )

    async def get_spot_delist_schedule(self, *, recv_window: int | None = None) -> Any:
        """

        GET /sapi/v1/spot/delist-schedule.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/others#get-symbols-delist-schedule-for-spot

        """
        return await self._native_public(
            "get_spot_delist_schedule", self._params(recvWindow=recv_window)
        )

    async def get_system_status(self) -> Any:
        """

        GET /sapi/v1/system/status.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/others#system-status

        """
        return await self._native_public("get_system_status", self._params())

    async def coin_futures_old_trades_lookup(
        self, *, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> Any:
        """

        Old Trades Lookup (MARKET_DATA).

        GET /dapi/v1/historicalTrades. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#old-trades-lookup

        """
        return await self._native_public(
            "coin_futures_old_trades_lookup",
            self._params(symbol=symbol, limit=limit, fromId=from_id),
        )

    async def query_coin_futures_index_price_constituents(self, *, symbol: str) -> Any:
        """

        Query Index Price Constituents.

        GET /dapi/v1/constituents. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#query-index-price-constituents

        """
        return await self._native_public(
            "query_coin_futures_index_price_constituents", self._params(symbol=symbol)
        )

    async def coin_futures_taker_buy_sell_volume(
        self,
        *,
        pair: str,
        contract_type: str,
        period: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:
        """

        Taker Buy/Sell Volume.

        GET /futures/data/takerBuySellVol. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#taker-buy-sell-volume

        """
        return await self._native_public(
            "coin_futures_taker_buy_sell_volume",
            self._params(
                pair=pair,
                contractType=contract_type,
                period=period,
                limit=limit,
                startTime=start_time,
                endTime=end_time,
            ),
        )

    async def coin_futures_test_connectivity(self) -> Any:
        """

        Test Connectivity.

        GET /dapi/v1/ping. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#test-connectivity

        """
        return await self._native_public("coin_futures_test_connectivity", self._params())

    async def pm_test_connectivity(self) -> Any:
        """

        Test Connectivity.

        GET /papi/v1/ping. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/market-data#test-connectivity

        """
        return await self._native_public("pm_test_connectivity", self._params())

    async def futures_list_all_convert_pairs(
        self, *, from_asset: str | None = None, to_asset: str | None = None
    ) -> Any:
        """

        List All Convert Pairs.

        GET /fapi/v1/convert/exchangeInfo. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#list-all-convert-pairs

        """
        return await self._native_public(
            "futures_list_all_convert_pairs", self._params(fromAsset=from_asset, toAsset=to_asset)
        )

    async def futures_adl_risk(self, *, symbol: str | None = None) -> Any:
        """

        ADL Risk.

        GET /fapi/v1/symbolAdlRisk. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#adl-risk

        """
        return await self._native_public("futures_adl_risk", self._params(symbol=symbol))

    async def futures_asset_index(self, *, symbol: str | None = None) -> Any:
        """

        Multi-Assets Mode Asset Index.

        GET /fapi/v1/assetIndex. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#asset-index

        """
        return await self._native_public("futures_asset_index", self._params(symbol=symbol))

    async def futures_composite_index_symbol_information(self, *, symbol: str | None = None) -> Any:
        """

        Composite Index Symbol Information.

        GET /fapi/v1/indexInfo. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#composite-index-symbol-information

        """
        return await self._native_public(
            "futures_composite_index_symbol_information", self._params(symbol=symbol)
        )

    async def futures_old_trades_lookup(
        self, *, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> Any:
        """

        Old Trades Lookup (MARKET_DATA).

        GET /fapi/v1/historicalTrades. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#old-trades-lookup

        """
        return await self._native_public(
            "futures_old_trades_lookup", self._params(symbol=symbol, limit=limit, fromId=from_id)
        )

    async def futures_quarterly_contract_settlement_price(self, *, pair: str) -> Any:
        """

        Quarterly Contract Settlement Price.

        GET /futures/data/delivery-price. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#quarterly-contract-settlement-price

        """
        return await self._native_public(
            "futures_quarterly_contract_settlement_price", self._params(pair=pair)
        )

    async def query_futures_index_price_constituents(self, *, symbol: str) -> Any:
        """

        Query Index Price Constituents.

        GET /fapi/v1/constituents. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#query-index-price-constituents

        """
        return await self._native_public(
            "query_futures_index_price_constituents", self._params(symbol=symbol)
        )

    async def query_futures_insurance_fund_balance_snapshot(
        self, *, symbol: str | None = None
    ) -> Any:
        """

        Query Insurance Fund Balance Snapshot.

        GET /fapi/v1/insuranceBalance. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#query-insurance-fund-balance-snapshot

        """
        return await self._native_public(
            "query_futures_insurance_fund_balance_snapshot", self._params(symbol=symbol)
        )

    async def futures_rpi_order_book(self, *, symbol: str, limit: int | None = None) -> Any:
        """

        RPI Order Book.

        GET /fapi/v1/rpiDepth. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#rpi-order-book

        """
        return await self._native_public(
            "futures_rpi_order_book", self._params(symbol=symbol, limit=limit)
        )

    async def futures_test_connectivity(self) -> Any:
        """

        Test Connectivity.

        GET /fapi/v1/ping. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#test-connectivity

        """
        return await self._native_public("futures_test_connectivity", self._params())

    async def futures_trading_schedule(self) -> Any:
        """

        Trading Schedule.

        GET /fapi/v1/tradingSchedule. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#trading-schedule

        """
        return await self._native_public("futures_trading_schedule", self._params())

    async def margin_cross_margin_collateral_ratio(self) -> Any:
        """

        Cross margin collateral ratio (MARKET_DATA).

        GET /sapi/v1/margin/crossMarginCollateralRatio. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#cross-margin-collateral-ratio

        """
        return await self._native_public("margin_cross_margin_collateral_ratio", self._params())

    async def get_margin_limit_price_pairs(self) -> Any:
        """

        Get Limit Price Pairs (MARKET_DATA).

        GET /sapi/v1/margin/limit-price-pairs. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-limit-price-pairs

        """
        return await self._native_public("get_margin_limit_price_pairs", self._params())

    async def get_margin_list_schedule(self, *, recv_window: int | None = None) -> Any:
        """

        Get list Schedule (MARKET_DATA).

        GET /sapi/v1/margin/list-schedule. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-list-schedule

        """
        return await self._native_public(
            "get_margin_list_schedule", self._params(recvWindow=recv_window)
        )

    async def get_margin_margin_asset_risk_based_liquidation_ratio(self) -> Any:
        """

        Get Margin Asset Risk-Based Liquidation Ratio (MARKET_DATA).

        GET /sapi/v1/margin/risk-based-liquidation-ratio. Native exchange symbols; decimal
        amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-margin-asset-risk-based-liquidation-ratio

        """
        return await self._native_public(
            "get_margin_margin_asset_risk_based_liquidation_ratio", self._params()
        )

    async def get_margin_margin_restricted_assets(self) -> Any:
        """

        Get Margin Restricted Assets (MARKET_DATA).

        GET /sapi/v1/margin/restricted-asset. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-margin-restricted-assets

        """
        return await self._native_public("get_margin_margin_restricted_assets", self._params())

    async def query_margin_liability_coin_leverage_bracket_in_cross_margin_pro_mode(self) -> Any:
        """

        Query Liability Coin Leverage Bracket in Cross Margin Pro Mode (MARKET_DATA).

        GET /sapi/v1/margin/leverageBracket. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#query-liability-coin-leverage-bracket-in-cross-margin-pro-mode

        """
        return await self._native_public(
            "query_margin_liability_coin_leverage_bracket_in_cross_margin_pro_mode", self._params()
        )

    async def spot_execution_rules(
        self,
        *,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        symbol_status: str | None = None,
    ) -> Any:
        """

        Query Execution Rules.

        GET /api/v3/executionRules. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general#execution-rules

        """
        return await self._native_public(
            "spot_execution_rules",
            self._params(
                symbol=symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                symbolStatus=symbol_status,
            ),
        )

    async def spot_ping(self) -> Any:
        """

        Test connectivity.

        GET /api/v3/ping. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general#ping

        """
        return await self._native_public("spot_ping", self._params())

    async def spot_historical_block_trades(
        self, *, symbol: str, from_id: int, limit: int | None = None
    ) -> Any:
        """

        Historical Block Trades (MARKET_DATA).

        GET /api/v3/historicalBlockTrades. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#historical-block-trades

        """
        return await self._native_public(
            "spot_historical_block_trades", self._params(symbol=symbol, fromId=from_id, limit=limit)
        )

    async def spot_historical_trades(
        self, *, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> Any:
        """

        Old trade lookup.

        GET /api/v3/historicalTrades. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#historical-trades

        """
        return await self._native_public(
            "spot_historical_trades", self._params(symbol=symbol, limit=limit, fromId=from_id)
        )

    async def spot_reference_price(self, *, symbol: str) -> Any:
        """

        Query Reference Price.

        GET /api/v3/referencePrice. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#reference-price

        """
        return await self._native_public("spot_reference_price", self._params(symbol=symbol))

    async def spot_reference_price_calculation(
        self, *, symbol: str, symbol_status: str | None = None
    ) -> Any:
        """

        Query Reference Price Calculation.

        GET /api/v3/referencePrice/calculation. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#reference-price-calculation

        """
        return await self._native_public(
            "spot_reference_price_calculation",
            self._params(symbol=symbol, symbolStatus=symbol_status),
        )

    async def spot_ticker(
        self,
        *,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        window_size: str | None = None,
        kind_type: str | None = None,
        symbol_status: str | None = None,
    ) -> Any:
        """

        Rolling window price change statistics.

        GET /api/v3/ticker. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ticker

        """
        return await self._native_public(
            "spot_ticker",
            self._params(
                symbol=symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                windowSize=window_size,
                type=kind_type,
                symbolStatus=symbol_status,
            ),
        )

    async def spot_ticker_trading_day(
        self,
        *,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        time_zone: str | None = None,
        kind_type: str | None = None,
        symbol_status: str | None = None,
    ) -> Any:
        """

        Trading Day Ticker.

        GET /api/v3/ticker/tradingDay. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ticker-trading-day

        """
        return await self._native_public(
            "spot_ticker_trading_day",
            self._params(
                symbol=symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                timeZone=time_zone,
                type=kind_type,
                symbolStatus=symbol_status,
            ),
        )

    async def spot_ui_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: str | None = None,
        limit: int | None = None,
    ) -> Any:
        """

        UIKlines.

        GET /api/v3/uiKlines. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ui-klines

        """
        return await self._native_public(
            "spot_ui_klines",
            self._params(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                timeZone=time_zone,
                limit=limit,
            ),
        )

    async def get_wallet_open_symbol_list(self) -> Any:
        """

        Get Open Symbol List (MARKET_DATA).

        GET /sapi/v1/spot/open-symbol-list. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#get-open-symbol-list

        """
        return await self._native_public("get_wallet_open_symbol_list", self._params())

    async def get_wallet_spot_asset_tags(self, *, tag: str | None = None) -> Any:
        """

        Get Spot Asset Tags (MARKET_DATA).

        GET /sapi/v1/spot/asset/tags. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#get-spot-asset-tags

        """
        return await self._native_public("get_wallet_spot_asset_tags", self._params(tag=tag))

    async def pm_pro_portfolio_margin_collateral_rate(self) -> Any:
        """

        Portfolio Margin Collateral Rate (MARKET_DATA).

        GET /sapi/v1/portfolio/collateralRate. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#portfolio-margin-collateral-rate

        """
        return await self._native_public("pm_pro_portfolio_margin_collateral_rate", self._params())

    async def query_pm_pro_portfolio_margin_asset_index_price(
        self, *, asset: str | None = None
    ) -> Any:
        """

        Query Portfolio Margin Asset Index Price (MARKET_DATA).

        GET /sapi/v1/portfolio/asset-index-price. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#query-portfolio-margin-asset-index-price

        """
        return await self._native_public(
            "query_pm_pro_portfolio_margin_asset_index_price", self._params(asset=asset)
        )
