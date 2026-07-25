"""Backpack async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Backpack public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a Backpack public WebSocket client."""
        self._native_client = _native.BackpackPublicWebSocketClient(
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send a WebSocket ping frame."""
        await self._native_client.ping()

    async def subscribe(self, streams: list[str]) -> None:
        """Subscribe to raw Backpack stream names."""
        await self._native_client.subscribe(streams)

    async def unsubscribe(self, streams: list[str]) -> None:
        """Unsubscribe from raw Backpack stream names."""
        await self._native_client.unsubscribe(streams)

    async def subscribe_book_ticker(self, product_symbol: str) -> None:
        """Subscribe to book ticker updates for a product."""
        await self._native_client.subscribe_book_ticker(product_symbol)

    async def subscribe_depth(self, product_symbol: str, speed: str | None = None) -> None:
        """Subscribe to depth updates for a product."""
        await self._native_client.subscribe_depth(product_symbol, speed)

    async def subscribe_orderbook(
        self,
        product_symbol: str,
        speed: str | None = None,
    ) -> None:
        """Subscribe to order book updates for a product."""
        await self._native_client.subscribe_orderbook(product_symbol, speed)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        """Subscribe to kline updates for a product."""
        await self._native_client.subscribe_klines(product_symbol, interval)

    async def subscribe_liquidation(self, product_symbol: str) -> None:
        """Subscribe to liquidation updates for a product."""
        await self._native_client.subscribe_liquidation(product_symbol)

    async def subscribe_mark_price(self, product_symbol: str) -> None:
        """Subscribe to mark price updates for a product."""
        await self._native_client.subscribe_mark_price(product_symbol)

    async def subscribe_ticker(self, product_symbol: str) -> None:
        """Subscribe to ticker updates for a product."""
        await self._native_client.subscribe_ticker(product_symbol)

    async def subscribe_open_interest(self, product_symbol: str) -> None:
        """Subscribe to open interest updates for a product."""
        await self._native_client.subscribe_open_interest(product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        """Subscribe to trade updates for a product."""
        await self._native_client.subscribe_trades(product_symbol)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Backpack WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Backpack private user WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        window: int = 5000,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a Backpack private WebSocket client."""
        self._native_client = _native.BackpackPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            window=window,
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send a WebSocket ping frame."""
        await self._native_client.ping()

    async def subscribe(self, streams: list[str]) -> None:
        """Subscribe to raw authenticated Backpack stream names."""
        await self._native_client.subscribe(streams)

    async def unsubscribe(self, streams: list[str]) -> None:
        """Unsubscribe from raw Backpack stream names."""
        await self._native_client.unsubscribe(streams)

    async def subscribe_orders(self, product_symbol: str | None = None) -> None:
        """Subscribe to order update events."""
        await self._native_client.subscribe_orders(product_symbol)

    async def subscribe_positions(self, product_symbol: str | None = None) -> None:
        """Subscribe to position update events."""
        await self._native_client.subscribe_positions(product_symbol)

    async def subscribe_rfq(self, product_symbol: str | None = None) -> None:
        """Subscribe to RFQ update events."""
        await self._native_client.subscribe_rfq(product_symbol)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Backpack WebSocket event payload: {event!r}")


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async Backpack public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    window: int = 5000,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PrivateClient:
    """Create an async Backpack private user WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        window=window,
        timeout=timeout,
        base_url=base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
