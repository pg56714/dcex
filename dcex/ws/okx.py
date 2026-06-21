"""OKX async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async OKX public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create an OKX public WebSocket client."""
        self._native_client = _native.OkxPublicWebSocketClient(
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def subscribe_channel(
        self,
        channel: str,
        product_symbol: str | None = None,
    ) -> None:
        """Subscribe to an OKX public channel."""
        await self._native_client.subscribe_channel(channel, product_symbol)

    async def unsubscribe_channel(
        self,
        channel: str,
        product_symbol: str | None = None,
    ) -> None:
        """Unsubscribe from an OKX public channel."""
        await self._native_client.unsubscribe_channel(channel, product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        """Subscribe to trade events for a product."""
        await self._native_client.subscribe_trades(product_symbol)

    async def subscribe_ticker(self, product_symbol: str) -> None:
        """Subscribe to ticker events for a product."""
        await self._native_client.subscribe_ticker(product_symbol)

    async def subscribe_orderbook(self, product_symbol: str) -> None:
        """Subscribe to order book events for a product."""
        await self._native_client.subscribe_orderbook(product_symbol)

    async def subscribe_orderbook5(self, product_symbol: str) -> None:
        """Subscribe to five-level order book events for a product."""
        await self._native_client.subscribe_orderbook5(product_symbol)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        """Subscribe to kline events for a product."""
        await self._native_client.subscribe_klines(product_symbol, interval)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected OKX WebSocket event payload: {event!r}")


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async OKX public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


__all__ = ["PublicClient", "public"]
