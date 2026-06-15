"""Kraken public market-data async HTTP client backed by Rust."""

from typing import Any

from ..._native_http import NativeResponse
from ...utils.common import Common
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
        status, headers, body = await self._native_client.public_request_async(method_name, params)
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    def _exchange_symbol(self, product_symbol: str) -> str:
        """Map product symbol through PTM when available."""
        if hasattr(self, "ptm"):
            return self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol)
        parts = product_symbol.split("-")
        if len(parts) >= 3:
            base = "XBT" if parts[0] == "BTC" else parts[0]
            quote = "XBT" if parts[1] == "BTC" else parts[1]
            prefix = "PF_" if parts[2] != "SPOT" else ""
            return f"{prefix}{base}{quote}"
        return product_symbol

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            if key == "from_":
                key = "from"
            if isinstance(value, bool):
                params.append((key, str(value).lower()))
            elif isinstance(value, (list, tuple)):
                params.extend((key, str(item)) for item in value)
            else:
                params.append((key, str(value)))
        return params

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
            self._params(pair=pair, info=info),
        )

    async def get_spot_ticker(
        self,
        product_symbol: str | None = None,
        pair: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot ticker data for one pair or all pairs."""
        if product_symbol is not None and pair is not None:
            raise ValueError("Specify either product_symbol or pair, not both.")
        resolved_pair = (
            self._exchange_symbol(product_symbol) if product_symbol is not None else pair
        )
        return await self._native_public("get_spot_ticker", self._params(pair=resolved_pair))

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        count: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot orderbook data."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(pair=self._exchange_symbol(product_symbol), count=count),
        )

    async def get_spot_public_trades(
        self,
        product_symbol: str,
        since: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot public trades."""
        return await self._native_public(
            "get_spot_public_trades",
            self._params(pair=self._exchange_symbol(product_symbol), since=since),
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
            self._params(
                pair=self._exchange_symbol(product_symbol),
                interval=interval,
                since=since,
            ),
        )

    async def get_futures_instruments(
        self,
        contractType: str | list[str] | None = None,
        expired: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures instruments."""
        return await self._native_public(
            "get_futures_instruments",
            self._params(contractType=contractType, expired=expired),
        )

    async def get_futures_tickers(
        self,
        product_symbol: str | None = None,
        contractType: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures ticker data for one symbol or all symbols."""
        symbol = self._exchange_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public(
            "get_futures_tickers",
            self._params(symbol=symbol, contractType=contractType),
        )

    async def get_futures_orderbook(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures orderbook data."""
        return await self._native_public(
            "get_futures_orderbook",
            self._params(symbol=self._exchange_symbol(product_symbol)),
        )

    async def get_futures_public_trades(
        self,
        product_symbol: str,
        lastTime: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures recent public trade history."""
        return await self._native_public(
            "get_futures_public_trades",
            self._params(symbol=self._exchange_symbol(product_symbol), lastTime=lastTime),
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
            self._params(
                symbol=self._exchange_symbol(product_symbol),
                timeframe=timeframe,
                tick_type=tick_type,
                from_=from_,
                to=to,
                count=count,
            ),
        )
