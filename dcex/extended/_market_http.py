"""Extended market HTTP client backed by Rust."""

from collections.abc import Sequence
from typing import Any

from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for Extended market endpoints."""

    def get_markets(self, market: str | Sequence[str] | None = None) -> Any:  # noqa: ANN401
        return self._native_public("get_markets", self._native_params(market=market))

    def get_assets(
        self,
        asset: str | Sequence[str] | None = None,
        type: str | None = None,  # noqa: A002
        collateral: bool | None = None,
    ) -> Any:  # noqa: ANN401
        return self._native_public(
            "get_assets",
            self._native_params(asset=asset, type=type, collateral=collateral),
        )

    def get_asset_index_price(self, asset: str) -> Any:  # noqa: ANN401
        return self._native_public("get_asset_index_price", self._native_params(asset=asset))

    def get_market_statistics(self, market: str) -> Any:  # noqa: ANN401
        return self._native_public(
            "get_market_statistics",
            self._native_params(market=market),
        )

    def get_order_book(self, market: str) -> Any:  # noqa: ANN401
        return self._native_public(
            "get_order_book",
            self._native_params(market=market),
        )

    def get_trades(self, market: str) -> Any:  # noqa: ANN401
        return self._native_public(
            "get_trades",
            self._native_params(market=market),
        )

    def get_candles(
        self,
        market: str,
        interval: str,
        candleType: str = "trades",  # noqa: N803
        limit: int | None = None,
        endTime: int | None = None,  # noqa: N803
    ) -> Any:  # noqa: ANN401
        if limit is None:
            raise ValueError("limit is required for Extended candles.")
        return self._native_public(
            "get_candles",
            self._native_params(
                market=market,
                candleType=candleType,
                interval=interval,
                limit=limit,
                endTime=endTime,
            ),
        )

    def get_funding(
        self,
        market: str,
        startTime: int,  # noqa: N803
        endTime: int,  # noqa: N803
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return self._native_public(
            "get_funding",
            self._native_params(
                market=market,
                startTime=startTime,
                endTime=endTime,
                cursor=cursor,
                limit=limit,
            ),
        )

    def get_open_interest(
        self,
        market: str,
        interval: str,
        startTime: int,  # noqa: N803
        endTime: int,  # noqa: N803
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return self._native_public(
            "get_open_interest",
            self._native_params(
                market=market,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )
