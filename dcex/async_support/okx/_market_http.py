"""OKX Market async HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ...utils.common import Common
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for OKX market data operations."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed OKX public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("OKX native client is required for market methods.")
        response, data = await request_native_json_async(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    def _exchange_symbol(self, product_symbol: str) -> str:
        """Map product symbol through PTM when available."""
        if hasattr(self, "ptm"):
            return self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        parts = product_symbol.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}-{parts[1]}" if parts[2] == "SPOT" else product_symbol
        return product_symbol

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            params.append((key, str(value)))
        return params

    async def get_candles_ticks(
        self,
        product_symbol: str,
        bar: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
        adjust: str | None = None,
    ) -> dict[str, Any]:
        """Get candlestick data."""
        return await self._native_public(
            "get_candles_ticks",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                bar=bar,
                after=after,
                before=before,
                limit=limit,
                adjust=adjust,
            ),
        )

    async def get_orderbook(
        self,
        product_symbol: str,
        sz: str | None = None,
    ) -> dict[str, Any]:
        """Get order book data."""
        return await self._native_public(
            "get_orderbook",
            self._params(instId=self._exchange_symbol(product_symbol), sz=sz),
        )

    async def get_tickers(
        self,
        instType: str,
        instFamily: str | None = None,
    ) -> dict[str, Any]:
        """Get ticker data."""
        return await self._native_public(
            "get_tickers",
            self._params(instType=instType, instFamily=instFamily),
        )

    async def get_public_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get public trades data."""
        return await self._native_public(
            "get_public_trades",
            self._params(instId=self._exchange_symbol(product_symbol), limit=limit),
        )
