"""Bybit Market HTTP client backed by Rust."""

from typing import Any

from .._native_http import request_native_json
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Bybit market data HTTP client."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Bybit public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Bybit native client is required for public market methods.")
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
            params.append((key, str(value)))
        return params

    def get_instruments_info(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        status: str | None = None,
        baseCoin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get instruments information."""
        return self._native_public(
            "get_instruments_info",
            self._params(
                category=category,
                product_symbol=product_symbol,
                status=status,
                baseCoin=baseCoin,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_kline(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get kline/candlestick data."""
        return self._native_public(
            "get_kline",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                limit=limit,
            ),
        )

    def get_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get order book data."""
        return self._native_public(
            "get_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    def get_tickers(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
    ) -> dict[str, Any]:
        """Get ticker information."""
        return self._native_public(
            "get_tickers",
            self._params(category=category, product_symbol=product_symbol, baseCoin=baseCoin),
        )

    def get_funding_rate_history(
        self,
        product_symbol: str,
        startTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get funding rate history."""
        return self._native_public(
            "get_funding_rate_history",
            self._params(product_symbol=product_symbol, startTime=startTime, limit=limit),
        )

    def get_public_trade_history(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get public trade history."""
        return self._native_public(
            "get_public_trade_history",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    def get_open_interest(
        self,
        product_symbol: str,
        intervalTime: str = "5min",
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get open interest history."""
        return self._native_public(
            "get_open_interest",
            self._params(
                product_symbol=product_symbol,
                intervalTime=intervalTime,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_long_short_ratio(
        self,
        product_symbol: str,
        period: str = "5min",
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get long/short account ratio history."""
        return self._native_public(
            "get_long_short_ratio",
            self._params(
                product_symbol=product_symbol,
                period=period,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_historical_volatility(
        self,
        category: str = "option",
        baseCoin: str | None = None,
        period: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get historical volatility data."""
        return self._native_public(
            "get_historical_volatility",
            self._params(
                category=category,
                baseCoin=baseCoin,
                period=period,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_insurance_pool(self, coin: str | None = None) -> dict[str, Any]:
        """Get insurance pool data."""
        return self._native_public("get_insurance_pool", self._params(coin=coin))

    def get_delivery_price(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get delivery price data."""
        return self._native_public(
            "get_delivery_price",
            self._params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_order_price_limit(
        self,
        product_symbol: str,
        category: str = "linear",
    ) -> dict[str, Any]:
        """Get order price limit data."""
        return self._native_public(
            "get_order_price_limit",
            self._params(category=category, product_symbol=product_symbol),
        )

    def get_adl_alert(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get ADL alert data."""
        return self._native_public(
            "get_adl_alert",
            self._params(category=category, product_symbol=product_symbol),
        )

    def get_risk_limit(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get risk limit information."""
        return self._native_public(
            "get_risk_limit",
            self._params(category=category, product_symbol=product_symbol, cursor=cursor),
        )
