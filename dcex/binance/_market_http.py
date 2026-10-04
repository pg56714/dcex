# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
"""Binance public market API wrappers backed by Rust."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

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
        kwargs = normalize_params(kwargs)
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
        """Get server time for spot, swap, coin_futures, equity, or options."""
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
        """
        Get kline/candlestick data from Binance.

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).
        """
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

    def get_futures_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get USDⓈ-M futures order book data from Binance."""
        return self._native_public(
            "get_futures_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

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

    def get_coin_futures_aggregate_trades(
        self,
        *,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/aggTrades.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#compressed-aggregate-trades-list

        """
        return self._native_public(
            "get_coin_futures_aggregate_trades",
            self._params(
                symbol=symbol, fromId=from_id, startTime=start_time, endTime=end_time, limit=limit
            ),
        )

    def get_coin_futures_continuous_klines(
        self,
        *,
        pair: str,
        contract_type: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/continuousKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#continuous-contract-kline-candlestick-data

        """
        return self._native_public(
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

    def get_coin_futures_funding_info(self) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/fundingInfo.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#get-funding-rate-info

        """
        return self._native_public("get_coin_futures_funding_info", self._params())

    def get_coin_futures_index_price_klines(
        self,
        *,
        pair: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/indexPriceKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#index-price-kline-candlestick-data

        """
        return self._native_public(
            "get_coin_futures_index_price_klines",
            self._params(
                pair=pair, interval=interval, startTime=start_time, endTime=end_time, limit=limit
            ),
        )

    def get_coin_futures_mark_price_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/markPriceKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#mark-price-kline-candlestick-data

        """
        return self._native_public(
            "get_coin_futures_mark_price_klines",
            self._params(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def get_coin_futures_open_interest(self, *, symbol: str) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/openInterest.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#open-interest

        """
        return self._native_public("get_coin_futures_open_interest", self._params(symbol=symbol))

    def get_coin_futures_premium_index_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/premiumIndexKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#premium-index-kline-data

        """
        return self._native_public(
            "get_coin_futures_premium_index_klines",
            self._params(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def get_coin_futures_book_ticker(
        self, *, symbol: str | None = None, pair: str | None = None
    ) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/ticker/bookTicker.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#symbol-order-book-ticker

        """
        return self._native_public(
            "get_coin_futures_book_ticker", self._params(symbol=symbol, pair=pair)
        )

    def get_coin_futures_24h_ticker(
        self, *, symbol: str | None = None, pair: str | None = None
    ) -> Any:  # noqa: ANN401
        """

        GET /dapi/v1/ticker/24hr.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#ticker24hr-price-change-statistics

        """
        return self._native_public(
            "get_coin_futures_24h_ticker", self._params(symbol=symbol, pair=pair)
        )

    def get_futures_aggregate_trades(
        self,
        *,
        product_symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/aggTrades.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#compressed-aggregate-trades-list

        """
        return self._native_public(
            "get_futures_aggregate_trades",
            self._params(
                product_symbol=product_symbol,
                fromId=from_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def get_futures_continuous_klines(
        self,
        *,
        pair: str,
        contract_type: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/continuousKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#continuous-contract-kline-candlestick-data

        """
        return self._native_public(
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

    def get_futures_funding_info(self) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/fundingInfo.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#get-funding-rate-info

        """
        return self._native_public("get_futures_funding_info", self._params())

    def get_futures_index_price_klines(
        self,
        *,
        pair: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/indexPriceKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#index-price-kline-candlestick-data

        """
        return self._native_public(
            "get_futures_index_price_klines",
            self._params(
                pair=pair, interval=interval, startTime=start_time, endTime=end_time, limit=limit
            ),
        )

    def get_futures_mark_price_klines(
        self,
        *,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/markPriceKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#mark-price-kline-candlestick-data

        """
        return self._native_public(
            "get_futures_mark_price_klines",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def get_futures_premium_index_klines(
        self,
        *,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/premiumIndexKlines.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#premium-index-kline-data

        """
        return self._native_public(
            "get_futures_premium_index_klines",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def get_futures_recent_trades(self, *, product_symbol: str, limit: int | None = None) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/trades.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#recent-trades-list

        """
        return self._native_public(
            "get_futures_recent_trades", self._params(product_symbol=product_symbol, limit=limit)
        )

    def get_futures_price_ticker_v1(self, *, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/ticker/price.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#symbol-price-ticker

        """
        return self._native_public(
            "get_futures_price_ticker_v1", self._params(product_symbol=product_symbol)
        )

    def get_futures_price_ticker(self, *, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """

        GET /fapi/v2/ticker/price.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#symbol-price-ticker-v2

        """
        return self._native_public(
            "get_futures_price_ticker", self._params(product_symbol=product_symbol)
        )

    def get_futures_24h_ticker(self, *, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """

        GET /fapi/v1/ticker/24hr.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#ticker24hr-price-change-statistics

        """
        return self._native_public(
            "get_futures_24h_ticker", self._params(product_symbol=product_symbol)
        )

    def get_margin_delist_schedule(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """

        GET /sapi/v1/margin/delist-schedule.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-delist-schedule

        """
        return self._native_public(
            "get_margin_delist_schedule", self._params(recvWindow=recv_window)
        )

    def get_spot_aggregate_trades(
        self,
        *,
        product_symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /api/v3/aggTrades.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#agg-trades

        """
        return self._native_public(
            "get_spot_aggregate_trades",
            self._params(
                product_symbol=product_symbol,
                fromId=from_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def get_spot_average_price(self, *, product_symbol: str) -> Any:  # noqa: ANN401
        """

        GET /api/v3/avgPrice.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#avg-price

        """
        return self._native_public(
            "get_spot_average_price", self._params(product_symbol=product_symbol)
        )

    def get_spot_24h_ticker(
        self,
        *,
        product_symbol: str | None = None,
        symbols: list[str] | None = None,
        kind_type: str | None = None,
        symbol_status: str | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /api/v3/ticker/24hr.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ticker24hr

        """
        return self._native_public(
            "get_spot_24h_ticker",
            self._params(
                product_symbol=product_symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                type=kind_type,
                symbolStatus=symbol_status,
            ),
        )

    def get_spot_book_ticker(
        self,
        *,
        product_symbol: str | None = None,
        symbols: list[str] | None = None,
        symbol_status: str | None = None,
    ) -> Any:  # noqa: ANN401
        """

        GET /api/v3/ticker/bookTicker.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ticker-book-ticker

        """
        return self._native_public(
            "get_spot_book_ticker",
            self._params(
                product_symbol=product_symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                symbolStatus=symbol_status,
            ),
        )

    def get_spot_delist_schedule(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """

        GET /sapi/v1/spot/delist-schedule.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/others#get-symbols-delist-schedule-for-spot

        """
        return self._native_public("get_spot_delist_schedule", self._params(recvWindow=recv_window))

    def get_system_status(self) -> Any:  # noqa: ANN401
        """

        GET /sapi/v1/system/status.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/others#system-status

        """
        return self._native_public("get_system_status", self._params())

    def coin_futures_old_trades_lookup(
        self, *, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> Any:  # noqa: ANN401
        """

        Old Trades Lookup (MARKET_DATA).

        GET /dapi/v1/historicalTrades. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#old-trades-lookup

        """
        return self._native_public(
            "coin_futures_old_trades_lookup",
            self._params(symbol=symbol, limit=limit, fromId=from_id),
        )

    def query_coin_futures_index_price_constituents(self, *, symbol: str) -> Any:  # noqa: ANN401
        """

        Query Index Price Constituents.

        GET /dapi/v1/constituents. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#query-index-price-constituents

        """
        return self._native_public(
            "query_coin_futures_index_price_constituents", self._params(symbol=symbol)
        )

    def coin_futures_taker_buy_sell_volume(
        self,
        *,
        pair: str,
        contract_type: str,
        period: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        Taker Buy/Sell Volume.

        GET /futures/data/takerBuySellVol. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#taker-buy-sell-volume

        """
        return self._native_public(
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

    def coin_futures_test_connectivity(self) -> Any:  # noqa: ANN401
        """

        Test Connectivity.

        GET /dapi/v1/ping. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#test-connectivity

        """
        return self._native_public("coin_futures_test_connectivity", self._params())

    def pm_test_connectivity(self) -> Any:  # noqa: ANN401
        """

        Test Connectivity.

        GET /papi/v1/ping. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/market-data#test-connectivity

        """
        return self._native_public("pm_test_connectivity", self._params())

    def futures_list_all_convert_pairs(
        self, *, from_asset: str | None = None, to_asset: str | None = None
    ) -> Any:  # noqa: ANN401
        """

        List All Convert Pairs.

        GET /fapi/v1/convert/exchangeInfo. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#list-all-convert-pairs

        """
        return self._native_public(
            "futures_list_all_convert_pairs", self._params(fromAsset=from_asset, toAsset=to_asset)
        )

    def futures_adl_risk(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """

        ADL Risk.

        GET /fapi/v1/symbolAdlRisk. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#adl-risk

        """
        return self._native_public("futures_adl_risk", self._params(symbol=symbol))

    def futures_asset_index(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """

        Multi-Assets Mode Asset Index.

        GET /fapi/v1/assetIndex. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#asset-index

        """
        return self._native_public("futures_asset_index", self._params(symbol=symbol))

    def futures_composite_index_symbol_information(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """

        Composite Index Symbol Information.

        GET /fapi/v1/indexInfo. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#composite-index-symbol-information

        """
        return self._native_public(
            "futures_composite_index_symbol_information", self._params(symbol=symbol)
        )

    def futures_old_trades_lookup(
        self, *, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> Any:  # noqa: ANN401
        """

        Old Trades Lookup (MARKET_DATA).

        GET /fapi/v1/historicalTrades. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#old-trades-lookup

        """
        return self._native_public(
            "futures_old_trades_lookup", self._params(symbol=symbol, limit=limit, fromId=from_id)
        )

    def futures_quarterly_contract_settlement_price(self, *, pair: str) -> Any:  # noqa: ANN401
        """

        Quarterly Contract Settlement Price.

        GET /futures/data/delivery-price. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#quarterly-contract-settlement-price

        """
        return self._native_public(
            "futures_quarterly_contract_settlement_price", self._params(pair=pair)
        )

    def query_futures_index_price_constituents(self, *, symbol: str) -> Any:  # noqa: ANN401
        """

        Query Index Price Constituents.

        GET /fapi/v1/constituents. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#query-index-price-constituents

        """
        return self._native_public(
            "query_futures_index_price_constituents", self._params(symbol=symbol)
        )

    def query_futures_insurance_fund_balance_snapshot(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """

        Query Insurance Fund Balance Snapshot.

        GET /fapi/v1/insuranceBalance. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#query-insurance-fund-balance-snapshot

        """
        return self._native_public(
            "query_futures_insurance_fund_balance_snapshot", self._params(symbol=symbol)
        )

    def futures_rpi_order_book(self, *, symbol: str, limit: int | None = None) -> Any:  # noqa: ANN401
        """

        RPI Order Book.

        GET /fapi/v1/rpiDepth. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#rpi-order-book

        """
        return self._native_public(
            "futures_rpi_order_book", self._params(symbol=symbol, limit=limit)
        )

    def futures_test_connectivity(self) -> Any:  # noqa: ANN401
        """

        Test Connectivity.

        GET /fapi/v1/ping. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#test-connectivity

        """
        return self._native_public("futures_test_connectivity", self._params())

    def futures_trading_schedule(self) -> Any:  # noqa: ANN401
        """

        Trading Schedule.

        GET /fapi/v1/tradingSchedule. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#trading-schedule

        """
        return self._native_public("futures_trading_schedule", self._params())

    def margin_cross_margin_collateral_ratio(self) -> Any:  # noqa: ANN401
        """

        Cross margin collateral ratio (MARKET_DATA).

        GET /sapi/v1/margin/crossMarginCollateralRatio. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#cross-margin-collateral-ratio

        """
        return self._native_public("margin_cross_margin_collateral_ratio", self._params())

    def get_margin_limit_price_pairs(self) -> Any:  # noqa: ANN401
        """

        Get Limit Price Pairs (MARKET_DATA).

        GET /sapi/v1/margin/limit-price-pairs. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-limit-price-pairs

        """
        return self._native_public("get_margin_limit_price_pairs", self._params())

    def get_margin_list_schedule(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """

        Get list Schedule (MARKET_DATA).

        GET /sapi/v1/margin/list-schedule. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-list-schedule

        """
        return self._native_public("get_margin_list_schedule", self._params(recvWindow=recv_window))

    def get_margin_margin_asset_risk_based_liquidation_ratio(self) -> Any:  # noqa: ANN401
        """

        Get Margin Asset Risk-Based Liquidation Ratio (MARKET_DATA).

        GET /sapi/v1/margin/risk-based-liquidation-ratio. Native exchange symbols; decimal
        amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-margin-asset-risk-based-liquidation-ratio

        """
        return self._native_public(
            "get_margin_margin_asset_risk_based_liquidation_ratio", self._params()
        )

    def get_margin_margin_restricted_assets(self) -> Any:  # noqa: ANN401
        """

        Get Margin Restricted Assets (MARKET_DATA).

        GET /sapi/v1/margin/restricted-asset. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-margin-restricted-assets

        """
        return self._native_public("get_margin_margin_restricted_assets", self._params())

    def query_margin_liability_coin_leverage_bracket_in_cross_margin_pro_mode(self) -> Any:  # noqa: ANN401
        """

        Query Liability Coin Leverage Bracket in Cross Margin Pro Mode (MARKET_DATA).

        GET /sapi/v1/margin/leverageBracket. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#query-liability-coin-leverage-bracket-in-cross-margin-pro-mode

        """
        return self._native_public(
            "query_margin_liability_coin_leverage_bracket_in_cross_margin_pro_mode", self._params()
        )

    def spot_execution_rules(
        self,
        *,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        symbol_status: str | None = None,
    ) -> Any:  # noqa: ANN401
        """

        Query Execution Rules.

        GET /api/v3/executionRules. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general#execution-rules

        """
        return self._native_public(
            "spot_execution_rules",
            self._params(
                symbol=symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                symbolStatus=symbol_status,
            ),
        )

    def spot_ping(self) -> Any:  # noqa: ANN401
        """

        Test connectivity.

        GET /api/v3/ping. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general#ping

        """
        return self._native_public("spot_ping", self._params())

    def spot_historical_block_trades(
        self, *, symbol: str, from_id: int, limit: int | None = None
    ) -> Any:  # noqa: ANN401
        """

        Historical Block Trades (MARKET_DATA).

        GET /api/v3/historicalBlockTrades. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#historical-block-trades

        """
        return self._native_public(
            "spot_historical_block_trades", self._params(symbol=symbol, fromId=from_id, limit=limit)
        )

    def spot_historical_trades(
        self, *, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> Any:  # noqa: ANN401
        """

        Old trade lookup.

        GET /api/v3/historicalTrades. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#historical-trades

        """
        return self._native_public(
            "spot_historical_trades", self._params(symbol=symbol, limit=limit, fromId=from_id)
        )

    def spot_reference_price(self, *, symbol: str) -> Any:  # noqa: ANN401
        """

        Query Reference Price.

        GET /api/v3/referencePrice. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#reference-price

        """
        return self._native_public("spot_reference_price", self._params(symbol=symbol))

    def spot_reference_price_calculation(
        self, *, symbol: str, symbol_status: str | None = None
    ) -> Any:  # noqa: ANN401
        """

        Query Reference Price Calculation.

        GET /api/v3/referencePrice/calculation. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#reference-price-calculation

        """
        return self._native_public(
            "spot_reference_price_calculation",
            self._params(symbol=symbol, symbolStatus=symbol_status),
        )

    def spot_ticker(
        self,
        *,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        window_size: str | None = None,
        kind_type: str | None = None,
        symbol_status: str | None = None,
    ) -> Any:  # noqa: ANN401
        """

        Rolling window price change statistics.

        GET /api/v3/ticker. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ticker

        """
        return self._native_public(
            "spot_ticker",
            self._params(
                symbol=symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                windowSize=window_size,
                type=kind_type,
                symbolStatus=symbol_status,
            ),
        )

    def spot_ticker_trading_day(
        self,
        *,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        time_zone: str | None = None,
        kind_type: str | None = None,
        symbol_status: str | None = None,
    ) -> Any:  # noqa: ANN401
        """

        Trading Day Ticker.

        GET /api/v3/ticker/tradingDay. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ticker-trading-day

        """
        return self._native_public(
            "spot_ticker_trading_day",
            self._params(
                symbol=symbol,
                symbols=dumps(symbols) if symbols is not None else None,
                timeZone=time_zone,
                type=kind_type,
                symbolStatus=symbol_status,
            ),
        )

    def spot_ui_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: str | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """

        UIKlines.

        GET /api/v3/uiKlines. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#ui-klines

        """
        return self._native_public(
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

    def get_wallet_open_symbol_list(self) -> Any:  # noqa: ANN401
        """

        Get Open Symbol List (MARKET_DATA).

        GET /sapi/v1/spot/open-symbol-list. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#get-open-symbol-list

        """
        return self._native_public("get_wallet_open_symbol_list", self._params())

    def get_wallet_spot_asset_tags(self, *, tag: str | None = None) -> Any:  # noqa: ANN401
        """

        Get Spot Asset Tags (MARKET_DATA).

        GET /sapi/v1/spot/asset/tags. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#get-spot-asset-tags

        """
        return self._native_public("get_wallet_spot_asset_tags", self._params(tag=tag))

    def pm_pro_portfolio_margin_collateral_rate(self) -> Any:  # noqa: ANN401
        """

        Portfolio Margin Collateral Rate (MARKET_DATA).

        GET /sapi/v1/portfolio/collateralRate. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#portfolio-margin-collateral-rate

        """
        return self._native_public("pm_pro_portfolio_margin_collateral_rate", self._params())

    def query_pm_pro_portfolio_margin_asset_index_price(self, *, asset: str | None = None) -> Any:  # noqa: ANN401
        """

        Query Portfolio Margin Asset Index Price (MARKET_DATA).

        GET /sapi/v1/portfolio/asset-index-price. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#query-portfolio-margin-asset-index-price

        """
        return self._native_public(
            "query_pm_pro_portfolio_margin_asset_index_price", self._params(asset=asset)
        )
