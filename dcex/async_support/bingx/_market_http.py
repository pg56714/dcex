"""BingX async market HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for BingX market-related API endpoints."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed BingX public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BingX native client is required for public market methods.")
        response, data = await request_native_json_async(
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

    async def get_swap_instrument_info(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get swap instrument information."""
        return await self._native_public(
            "get_swap_instrument_info",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_instrument_info(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get spot instrument information."""
        return await self._native_public(
            "get_spot_instrument_info",
            self._params(product_symbol=product_symbol),
        )

    async def get_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get order book data."""
        return await self._native_public(
            "get_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get spot order book data."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def get_spot_orderbook_v2(
        self,
        product_symbol: str,
        limit: int | None = None,
        type_: str = "step0",
        depth: int | None = None,
    ) -> dict:
        """Get spot v2 order book data."""
        return await self._native_public(
            "get_spot_orderbook_v2",
            self._params(
                product_symbol=product_symbol,
                limit=limit,
                type_=type_,
                depth=depth,
            ),
        )

    async def get_public_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get public trade data."""
        return await self._native_public(
            "get_public_trades",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def get_spot_public_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get spot public trade data."""
        return await self._native_public(
            "get_spot_public_trades",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def get_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get kline/candlestick data."""
        return await self._native_public(
            "get_kline",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    async def get_spot_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get spot kline/candlestick data."""
        return await self._native_public(
            "get_spot_kline",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    async def get_spot_kline_v2(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get spot v2 kline/candlestick data."""
        return await self._native_public(
            "get_spot_kline_v2",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    async def get_open_interest(self, product_symbol: str) -> dict:
        """Get swap open interest."""
        return await self._native_public(
            "get_open_interest",
            self._params(product_symbol=product_symbol),
        )

    async def get_mark_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get swap mark price kline data."""
        return await self._native_public(
            "get_mark_price_kline",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    async def get_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get 24hr ticker price change statistics."""
        return await self._native_public(
            "get_ticker",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get spot 24hr ticker statistics."""
        return await self._native_public(
            "get_spot_ticker",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_book_ticker(
        self,
        product_symbol: str,
    ) -> dict:
        """Get spot best bid/ask ticker."""
        return await self._native_public(
            "get_spot_book_ticker",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_price_ticker(
        self,
        product_symbol: str,
    ) -> dict:
        """Get spot latest price ticker."""
        return await self._native_public(
            "get_spot_price_ticker",
            self._params(product_symbol=product_symbol),
        )
