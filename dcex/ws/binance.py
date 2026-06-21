"""Binance async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Binance public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a Binance public WebSocket client."""
        self._native_client = _native.BinancePublicWebSocketClient(
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def subscribe(self, streams: list[str]) -> int:
        """Subscribe to raw Binance stream names."""
        return int(await self._native_client.subscribe(streams))

    async def unsubscribe(self, streams: list[str]) -> int:
        """Unsubscribe from raw Binance stream names."""
        return int(await self._native_client.unsubscribe(streams))

    async def subscribe_trades(self, product_symbol: str) -> int:
        """Subscribe to raw trade events for a product."""
        return int(await self._native_client.subscribe_trades(product_symbol))

    async def subscribe_agg_trades(self, product_symbol: str) -> int:
        """Subscribe to aggregate trade events for a product."""
        return int(await self._native_client.subscribe_agg_trades(product_symbol))

    async def subscribe_orderbook(self, product_symbol: str) -> int:
        """Subscribe to diff order book events for a product."""
        return int(await self._native_client.subscribe_orderbook(product_symbol))

    async def subscribe_ticker(self, product_symbol: str) -> int:
        """Subscribe to ticker events for a product."""
        return int(await self._native_client.subscribe_ticker(product_symbol))

    async def subscribe_klines(self, product_symbol: str, interval: str) -> int:
        """Subscribe to kline events for a product."""
        return int(await self._native_client.subscribe_klines(product_symbol, interval))

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Binance WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Binance futures private user data WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        """Create a Binance private WebSocket client."""
        self._native_client = _native.BinancePrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            futures_http_base_url=futures_http_base_url,
            ws_base_url=ws_base_url,
        )

    async def connect(self) -> str:
        """Open the WebSocket connection and return the listen key."""
        return str(await self._native_client.connect())

    async def close(self) -> None:
        """Close the WebSocket connection and invalidate the listen key."""
        await self._native_client.close()

    async def keep_alive(self) -> None:
        """Extend the current listen key validity."""
        await self._native_client.keep_alive()

    async def close_listen_key(self) -> None:
        """Invalidate the current listen key."""
        await self._native_client.close_listen_key()

    def listen_key(self) -> str | None:
        """Return the current listen key if connected."""
        value = self._native_client.listen_key()
        return str(value) if value is not None else None

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Binance WebSocket event payload: {event!r}")


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async Binance public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    timeout: float = 10.0,
    spot_http_base_url: str | None = None,
    futures_http_base_url: str | None = None,
    ws_base_url: str | None = None,
) -> PrivateClient:
    """Create an async Binance futures private user data WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        timeout=timeout,
        spot_http_base_url=spot_http_base_url,
        futures_http_base_url=futures_http_base_url,
        ws_base_url=ws_base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
