"""Generated binance alpha HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedAlphaHTTP(MarketHTTP, TradeHTTP):
    """Alpha API methods."""

    def alpha_aggregated_trades(
        self,
        *,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Aggregated Trades.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#aggregated-trades
        """
        return self._native_public(
            "alpha_aggregated_trades",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "symbol": symbol,
                        "fromId": from_id,
                        "startTime": start_time,
                        "endTime": end_time,
                        "limit": limit,
                    }
                ).items()
                if value is not None
            ],
        )

    def alpha_full_depth(self, *, symbol: str, limit: str | None = None) -> Any:  # noqa: ANN401
        """
        Full Depth.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#full-depth
        """
        return self._native_public(
            "alpha_full_depth",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"symbol": symbol, "limit": limit}).items()
                if value is not None
            ],
        )

    def alpha_get_exchange_info(self) -> Any:  # noqa: ANN401
        """
        Get Exchange Info.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#get-exchange-info
        """
        return self._native_public(
            "alpha_get_exchange_info",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({}).items()
                if value is not None
            ],
        )

    def alpha_klines(
        self,
        *,
        symbol: str,
        interval: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Klines.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#klines
        """
        return self._native_public(
            "alpha_klines",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "symbol": symbol,
                        "interval": interval,
                        "limit": limit,
                        "startTime": start_time,
                        "endTime": end_time,
                    }
                ).items()
                if value is not None
            ],
        )

    def alpha_ticker(self, *, symbol: str) -> Any:  # noqa: ANN401
        """
        Ticker.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#ticker
        """
        return self._native_public(
            "alpha_ticker",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"symbol": symbol}).items()
                if value is not None
            ],
        )

    def alpha_token_list(self) -> Any:  # noqa: ANN401
        """
        Token List.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#token-list
        """
        return self._native_public(
            "alpha_token_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({}).items()
                if value is not None
            ],
        )
