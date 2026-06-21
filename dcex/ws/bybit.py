"""Bybit async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Bybit public market WebSocket client."""

    def __init__(
        self,
        category: str = "linear",
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a Bybit public WebSocket client."""
        self._native_client = _native.BybitPublicWebSocketClient(
            category=category,
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def subscribe(self, topics: list[str]) -> str:
        """Subscribe to raw Bybit topics."""
        return str(await self._native_client.subscribe(topics))

    async def unsubscribe(self, topics: list[str]) -> str:
        """Unsubscribe from raw Bybit topics."""
        return str(await self._native_client.unsubscribe(topics))

    async def ping(self) -> str:
        """Send an application-level ping."""
        return str(await self._native_client.ping())

    async def subscribe_trades(self, product_symbol: str) -> str:
        """Subscribe to trade events for a product."""
        return str(await self._native_client.subscribe_trades(product_symbol))

    async def subscribe_ticker(self, product_symbol: str) -> str:
        """Subscribe to ticker events for a product."""
        return str(await self._native_client.subscribe_ticker(product_symbol))

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 1) -> str:
        """Subscribe to order book events for a product."""
        return str(await self._native_client.subscribe_orderbook(product_symbol, depth))

    async def subscribe_klines(self, product_symbol: str, interval: str) -> str:
        """Subscribe to kline events for a product."""
        return str(await self._native_client.subscribe_klines(product_symbol, interval))

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Bybit WebSocket event payload: {event!r}")


def public(
    category: str = "linear",
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PublicClient:
    """Create an async Bybit public market WebSocket client."""
    return PublicClient(category=category, timeout=timeout, base_url=base_url)


__all__ = ["PublicClient", "public"]
