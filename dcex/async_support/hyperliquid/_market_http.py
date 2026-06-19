"""Market-related HTTP API client for Hyperliquid exchange backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for market-related operations on Hyperliquid exchange."""

    async def get_meta(self, dex: str | None = None) -> dict[str, Any]:
        """Get market metadata."""
        return await self._native_public("get_meta", self._native_params(dex=dex))

    async def get_spot_meta(self) -> dict[str, Any]:
        """Get spot market metadata."""
        return await self._native_public("get_spot_meta", [])

    async def get_meta_and_asset_ctxs(self) -> dict[str, Any]:
        """Get market metadata and asset contexts."""
        return await self._native_public("get_meta_and_asset_ctxs", [])

    async def get_spot_meta_and_asset_ctxs(self) -> dict[str, Any]:
        """Get spot market metadata and asset contexts."""
        return await self._native_public("get_spot_meta_and_asset_ctxs", [])

    async def get_l2book(self, product_symbol: str) -> dict[str, Any]:
        """Get L2 order book for a product."""
        return await self._native_public(
            "get_l2book",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_candle_snapshot(
        self,
        product_symbol: str,
        interval: str,
        startTime: int,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get candlestick data for a product."""
        return await self._native_public(
            "get_candle_snapshot",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_funding_rate_history(
        self,
        product_symbol: str,
        startTime: int,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get funding rate history for a product."""
        return await self._native_public(
            "get_funding_rate_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
            ),
        )
