"""Public Ondo market methods."""

# ruff: noqa: ANN401

from typing import Any

from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    def get_status(self) -> Any:
        return self._native_public("get_status")

    def get_markets(self) -> Any:
        return self._native_public("get_markets")

    def get_trades(self, market: str, limit: int | None = None, cursor: str | None = None) -> Any:
        return self._native_public("get_trades", market=market, limit=limit, cursor=cursor)

    def get_depth(self, market: str, depth: int | None = None) -> Any:
        return self._native_public("get_depth", market=market, depth=depth)

    def get_symbol_info(self) -> Any:
        return self._native_public("get_symbol_info")

    def get_funding_rates(self, market: str) -> Any:
        return self._native_public("get_funding_rates", market=market)

    def get_funding_rate_history(
        self,
        market: str,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return self._native_public(
            "get_funding_rate_history",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    def get_mark_prices(self) -> Any:
        return self._native_public("get_mark_prices")

    def get_open_interest(self) -> Any:
        return self._native_public("get_open_interest")

    def get_volume(self) -> Any:
        return self._native_public("get_volume")

    def get_contracts(self, sparkline: bool | None = None) -> Any:
        return self._native_public("get_contracts", sparkline=sparkline)

    def get_price_history(
        self,
        symbol: str,
        resolution: str,
        from_time: int,
        to_time: int,
    ) -> Any:
        """Use a TradingView symbol such as BTCUSD.P and Unix seconds."""
        return self._native_public(
            "get_price_history",
            symbol=symbol,
            resolution=resolution,
            from_time=from_time,
            to_time=to_time,
        )
