"""Generated bingx market HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedMarketHTTP(MarketHTTP):
    """Market API methods."""

    def get_spot_v2_quote_price(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """
        Symbol Price Ticker.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Symbol%20Price%20Ticker
        """
        return self._native_public(
            "get_spot_v2_quote_price", self._native_params(**{"symbol": symbol})
        )

    def get_spot_v2_quote_book_ticker(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """
        Symbol Order Book Ticker.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Symbol%20Order%20Book%20Ticker
        """
        return self._native_public(
            "get_spot_v2_quote_book_ticker", self._native_params(**{"symbol": symbol})
        )

    def get_spot_v2_quote_depth(self, *, symbol: str, type_: str, limit: int | None = None) -> Any:  # noqa: ANN401
        """
        Order Book aggregation.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Order%20Book%20aggregation
        """
        return self._native_public(
            "get_spot_v2_quote_depth",
            self._native_params(**{"symbol": symbol, "type": type_, "limit": limit}),
        )

    def get_spot_v2_quote_historical_trades(
        self, *, symbol: str, limit: int | None = None, from_id: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Historical Trades.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Historical%20Trades
        """
        return self._native_public(
            "get_spot_v2_quote_historical_trades",
            self._native_params(**{"symbol": symbol, "limit": limit, "fromId": from_id}),
        )

    def get_spot_v2_quote_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Kline/Candlestick Data.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Kline%2FCandlestick%20Data
        """
        return self._native_public(
            "get_spot_v2_quote_klines",
            self._native_params(
                **{
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "timeZone": time_zone,
                    "limit": limit,
                }
            ),
        )

    def get_spot_v2_quote_ticker(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """
        24hr Ticker Price Change Statistics.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/24hr%20Ticker%20Price%20Change%20Statistics
        """
        return self._native_public(
            "get_spot_v2_quote_ticker", self._native_params(**{"symbol": symbol})
        )

    def get_spot_v2_quote_historical_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Historical K-line.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Historical%20K-line
        """
        return self._native_public(
            "get_spot_v2_quote_historical_klines",
            self._native_params(
                **{
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    def post_api_lindorm_v1_ai_kline_query(
        self,
        *,
        indicator_type: str,
        access_token: str,
        proxy_user: str,
        symbol: str | None = None,
        interval: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: str | None = None,
        size: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Internal Lindorm Query.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/bingx-trading-plan/api-reference.md#L3
        """
        return self._native_private(
            "post_api_lindorm_v1_ai_kline_query",
            self._native_params(
                **{
                    "indicatorType": indicator_type,
                    "access_token": access_token,
                    "proxy_user": proxy_user,
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "offset": offset,
                    "size": size,
                }
            ),
        )
