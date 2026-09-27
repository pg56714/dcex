"""Extended async market HTTP client backed by Rust."""

from collections.abc import Sequence
from typing import Any

from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for Extended market endpoints."""

    async def get_markets(
        self,
        market: str | Sequence[str] | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_public(
            "get_markets",
            self._native_params(market=market),
        )

    async def get_assets(
        self,
        asset: str | Sequence[str] | None = None,
        type: str | None = None,  # noqa: A002
        collateral: bool | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_public(
            "get_assets",
            self._native_params(asset=asset, type=type, collateral=collateral),
        )

    async def get_asset_index_price(self, asset: str) -> Any:  # noqa: ANN401
        return await self._native_public("get_asset_index_price", self._native_params(asset=asset))

    async def get_market_statistics(self, market: str) -> Any:  # noqa: ANN401
        return await self._native_public(
            "get_market_statistics",
            self._native_params(market=market),
        )

    async def get_order_book(self, market: str) -> Any:  # noqa: ANN401
        return await self._native_public(
            "get_order_book",
            self._native_params(market=market),
        )

    async def get_trades(self, market: str) -> Any:  # noqa: ANN401
        return await self._native_public(
            "get_trades",
            self._native_params(market=market),
        )

    async def get_candles(
        self,
        market: str,
        interval: str,
        candleType: str = "trades",  # noqa: N803
        limit: int | None = None,
        endTime: int | None = None,  # noqa: N803
    ) -> Any:  # noqa: ANN401
        return await self._native_public(
            "get_candles",
            self._native_params(
                market=market,
                candleType=candleType,
                interval=interval,
                limit=limit,
                endTime=endTime,
            ),
        )

    async def get_funding(
        self,
        market: str,
        startTime: int,  # noqa: N803
        endTime: int,  # noqa: N803
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_public(
            "get_funding",
            self._native_params(
                market=market,
                startTime=startTime,
                endTime=endTime,
                cursor=cursor,
                limit=limit,
            ),
        )

    async def get_open_interest(
        self,
        market: str,
        interval: str,
        startTime: int,  # noqa: N803
        endTime: int,  # noqa: N803
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_public(
            "get_open_interest",
            self._native_params(
                market=market,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_interest_rate_curves_history(self, *, interval: str) -> Any:  # noqa: ANN401
        """
        Get interest rate curves history.

        Source: https://api.docs.extended.exchange/#get-interest-rate-curves-history
        """
        return await self._native_public(
            "get_interest_rate_curves_history", self._native_params(interval=interval)
        )

    async def get_latest_interest_rate_curve(self) -> Any:  # noqa: ANN401
        """
        Get latest interest rate curve.

        Source: https://api.docs.extended.exchange/#get-latest-interest-rate-curve
        """
        return await self._native_public("get_latest_interest_rate_curve", self._native_params())

    async def get_vault_performance(self, *, interval: str) -> Any:  # noqa: ANN401
        """GET /api/v1/vault/public/performance."""
        return await self._native_public(
            "get_vault_performance", self._native_params(interval=interval)
        )

    async def get_vault_summary(self) -> Any:  # noqa: ANN401
        """GET /api/v1/vault/public/summary."""
        return await self._native_public("get_vault_summary", self._native_params())
