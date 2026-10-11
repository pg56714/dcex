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

    def hello(self) -> Any:
        """Get the public service greeting and health response."""
        return self._native_public("hello")

    def get_login_challenge(self, wallet_address: str, chain_id: str) -> Any:
        """Request a SIWE challenge for Ethereum (1) or Avalanche (43114)."""
        return self._native_public(
            "get_login_challenge", walletAddress=wallet_address, chainId=chain_id
        )

    def complete_login_challenge(self, id: str, signature: str, source: str | None = None) -> Any:
        """Exchange a caller-signed SIWE challenge for a JWT."""
        return self._native_public(
            "complete_login_challenge", id=id, signature=signature, source=source
        )

    def get_spot_depth(self, market: str, depth: int | None = None) -> Any:
        """Read spot depth (1 to 100 levels) using BASE-QUOTE or BASE-QUOTE-SPOT."""
        return self._native_public("get_spot_depth", market=market, depth=depth)

    def get_spot_trades(
        self, market: str, cursor: str | None = None, limit: int | None = None
    ) -> Any:
        """Read public spot trades; pass the previous nextCursor to page back."""
        return self._native_public("get_spot_trades", market=market, cursor=cursor, limit=limit)

    def get_spot_ticker(self, sparkline: bool | None = None) -> Any:
        """GET /v1/spot/ticker: 24h statistics for every Spot market, optionally with sparklines."""
        return self._native_public("get_spot_ticker", sparkline=sparkline)

    def get_spot_symbol_info(self) -> Any:
        """List spot TradingView symbols such as SPYUSDC."""
        return self._native_public("get_spot_symbol_info")

    def get_spot_price_history(
        self,
        symbol: str,
        resolution: str,
        to_time: int,
        from_time: int | None = None,
        countback: int | None = None,
    ) -> Any:
        """Read spot history ending at ``to_time``; give exactly one of from_time or countback."""
        return self._native_public(
            "get_spot_price_history",
            symbol=symbol,
            resolution=resolution,
            countback=countback,
            **{"from": from_time, "to": to_time},
        )
