"""Asynchronous public Ondo market methods."""

# ruff: noqa: ANN401

from typing import Any

from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    async def get_status(self) -> Any:
        return await self._native_public("get_status")

    async def get_markets(self) -> Any:
        return await self._native_public("get_markets")

    async def get_trades(
        self,
        market: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Any:
        return await self._native_public(
            "get_trades",
            market=market,
            limit=limit,
            cursor=cursor,
        )

    async def get_depth(self, market: str, depth: int | None = None) -> Any:
        return await self._native_public("get_depth", market=market, depth=depth)

    async def get_symbol_info(self) -> Any:
        return await self._native_public("get_symbol_info")

    async def get_funding_rates(self, market: str) -> Any:
        return await self._native_public("get_funding_rates", market=market)

    async def get_funding_rate_history(
        self,
        market: str,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return await self._native_public(
            "get_funding_rate_history",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    async def get_mark_prices(self) -> Any:
        return await self._native_public("get_mark_prices")

    async def get_open_interest(self) -> Any:
        return await self._native_public("get_open_interest")

    async def get_volume(self) -> Any:
        return await self._native_public("get_volume")

    async def get_contracts(self, sparkline: bool | None = None) -> Any:
        return await self._native_public("get_contracts", sparkline=sparkline)

    async def get_price_history(
        self,
        symbol: str,
        resolution: str,
        from_time: int,
        to_time: int,
    ) -> Any:
        """Use a TradingView symbol such as BTCUSD.P and Unix seconds."""
        return await self._native_public(
            "get_price_history",
            symbol=symbol,
            resolution=resolution,
            from_time=from_time,
            to_time=to_time,
        )

    async def hello(self) -> Any:
        """Get the public service greeting and health response."""
        return await self._native_public("hello")

    async def ping(self) -> Any:
        """Alias for the public /hello service check."""
        return await self._native_public("ping")

    async def get_login_challenge(self, wallet_address: str, chain_id: str) -> Any:
        """Request a SIWE challenge for Ethereum (1) or Avalanche (43114)."""
        return await self._native_public(
            "get_login_challenge", walletAddress=wallet_address, chainId=chain_id
        )

    async def complete_login_challenge(
        self, id: str, signature: str, source: str | None = None
    ) -> Any:
        """Exchange a caller-signed SIWE challenge for a JWT."""
        return await self._native_public(
            "complete_login_challenge", id=id, signature=signature, source=source
        )

    async def get_spot_depth(self, market: str) -> Any:
        """Read spot depth using BASE-QUOTE or BASE-QUOTE-SPOT."""
        return await self._native_public("get_spot_depth", market=market)

    async def get_spot_trades(self, market: str) -> Any:
        """Read public spot trades without account authentication."""
        return await self._native_public("get_spot_trades", market=market)

    async def get_spot_symbol_info(self) -> Any:
        """List spot TradingView symbols such as SPYUSDC."""
        return await self._native_public("get_spot_symbol_info")

    async def get_spot_price_history(
        self, symbol: str, resolution: str, from_time: int, to_time: int
    ) -> Any:
        """Read spot history with a TradingView symbol and Unix-second bounds."""
        return await self._native_public(
            "get_spot_price_history",
            symbol=symbol,
            resolution=resolution,
            **{"from": from_time, "to": to_time},
        )
