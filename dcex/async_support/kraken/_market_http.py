"""Kraken public market-data async HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for Kraken public market-data APIs."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Kraken public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Kraken native client is required for public market methods.")
        response, data = await request_native_json_async(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    async def get_server_time(self) -> dict[str, Any]:
        """Retrieve Kraken spot server time."""
        return await self._native_public("get_server_time", [])

    async def get_spot_asset_pairs(
        self,
        pair: str | None = None,
        info: str = "info",
    ) -> dict[str, Any]:
        """Retrieve Kraken spot tradable asset pairs."""
        return await self._native_public(
            "get_spot_asset_pairs",
            self._native_params(pair=pair, info=info),
        )

    async def get_spot_ticker(
        self,
        product_symbol: str | None = None,
        pair: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot ticker data for one pair or all pairs."""
        if product_symbol is not None and pair is not None:
            raise ValueError("Specify either product_symbol or pair, not both.")
        return await self._native_public(
            "get_spot_ticker",
            self._native_params(product_symbol=product_symbol, pair=pair),
        )

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        count: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot orderbook data."""
        return await self._native_public(
            "get_spot_orderbook",
            self._native_params(product_symbol=product_symbol, count=count),
        )

    async def get_spot_public_trades(
        self,
        product_symbol: str,
        since: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot public trades."""
        return await self._native_public(
            "get_spot_public_trades",
            self._native_params(product_symbol=product_symbol, since=since),
        )

    async def get_spot_kline(
        self,
        product_symbol: str,
        interval: int = 1,
        since: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot OHLC candles."""
        return await self._native_public(
            "get_spot_kline",
            self._native_params(product_symbol=product_symbol, interval=interval, since=since),
        )

    async def get_futures_instruments(
        self,
        contractType: str | list[str] | None = None,
        expired: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures instruments."""
        return await self._native_public(
            "get_futures_instruments",
            self._native_params(contractType=contractType, expired=expired),
        )

    async def get_futures_tickers(
        self,
        product_symbol: str | None = None,
        contractType: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures ticker data for one symbol or all symbols."""
        return await self._native_public(
            "get_futures_tickers",
            self._native_params(product_symbol=product_symbol, contractType=contractType),
        )

    async def get_futures_orderbook(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures orderbook data."""
        return await self._native_public(
            "get_futures_orderbook",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_public_trades(
        self,
        product_symbol: str,
        lastTime: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures recent public trade history."""
        return await self._native_public(
            "get_futures_public_trades",
            self._native_params(product_symbol=product_symbol, lastTime=lastTime),
        )

    async def get_futures_kline(
        self,
        product_symbol: str,
        timeframe: str,
        tick_type: str = "trade",
        from_: int | None = None,
        to: int | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures chart candles."""
        return await self._native_public(
            "get_futures_kline",
            self._native_params(
                product_symbol=product_symbol,
                timeframe=timeframe,
                tick_type=tick_type,
                from_=from_,
                to=to,
                count=count,
            ),
        )
