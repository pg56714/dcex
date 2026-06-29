import json
from typing import Any

from ..._native_http import request_native_json_async
from ...utils.common import Common
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for BitMEX market data API endpoints."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed BitMEX public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BitMEX native client is required for public market methods.")
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
            return self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        parts = product_symbol.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}{parts[1]}"
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

    async def get_instrument_info(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """Get instrument information for trading pairs."""
        return await self._native_public(
            "get_instrument_info",
            self._params(
                product_symbol=(
                    self._exchange_symbol(product_symbol) if product_symbol is not None else None
                ),
                filter=json.dumps(filter, separators=(",", ":")) if filter is not None else None,
                count=count,
            ),
        )

    async def get_orderbook(
        self,
        product_symbol: str,
        depth: int | None = None,
    ) -> dict[str, Any]:
        """Get orderbook data for a specific trading pair."""
        return await self._native_public(
            "get_orderbook",
            self._params(product_symbol=self._exchange_symbol(product_symbol), depth=depth),
        )

    async def get_trades(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """Get recent trade data."""
        return await self._native_public(
            "get_trades",
            self._params(
                product_symbol=(
                    self._exchange_symbol(product_symbol) if product_symbol is not None else None
                ),
                filter=str(filter) if filter is not None else None,
                columns=columns,
                count=count,
                start=start,
                reverse=reverse,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_ticker(
        self,
        binSize: str | None = None,
        partial: bool | None = None,
        symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """Get ticker data for trading pairs."""
        return await self._native_public(
            "get_ticker",
            self._params(
                binSize=binSize,
                partial=partial,
                symbol=self._exchange_symbol(symbol) if symbol is not None else None,
                filter=str(filter) if filter is not None else None,
                columns=columns,
                count=count,
                start=start,
                reverse=reverse,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_kline(
        self,
        binSize: str | None = None,
        partial: bool | None = None,
        symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """Get kline/candlestick data for trading pairs."""
        return await self._native_public(
            "get_kline",
            self._params(
                binSize=binSize,
                partial=partial,
                symbol=self._exchange_symbol(symbol) if symbol is not None else None,
                filter=str(filter) if filter is not None else None,
                columns=columns,
                count=count,
                start=start,
                reverse=reverse,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_funding(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """Get funding rate data for perpetual contracts."""
        return await self._native_public(
            "get_funding",
            self._params(
                product_symbol=(
                    self._exchange_symbol(product_symbol) if product_symbol is not None else None
                ),
                filter=str(filter) if filter is not None else None,
                columns=columns,
                count=count,
                start=start,
                reverse=reverse,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_liquidations(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        columns: str | None = None,
        count: int | None = None,
        start: int | None = None,
        reverse: bool | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
    ) -> dict[str, Any]:
        """Get liquidation orders."""
        return await self._native_public(
            "get_liquidations",
            self._params(
                product_symbol=(
                    self._exchange_symbol(product_symbol) if product_symbol is not None else None
                ),
                filter=json.dumps(filter, separators=(",", ":")) if filter is not None else None,
                columns=columns,
                count=count,
                start=start,
                reverse=reverse,
                startTime=startTime,
                endTime=endTime,
            ),
        )
