"""Gate.io async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


def _decode_event(body: bytes | bytearray | memoryview) -> dict[str, Any] | list[Any]:
    event = json.loads(bytes(body))
    if isinstance(event, dict | list):
        return event
    raise RuntimeError(f"Unexpected Gate.io WebSocket event payload: {event!r}")


class PublicClient(AsyncWebSocketMixin):
    """Async Gate.io public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a Gate.io public WebSocket client."""
        self._native_client = _native.GateioPublicWebSocketClient(
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
        """Send a ping request."""
        await self._native_client.ping()

    async def subscribe(self, channel: str, payload: list[str]) -> None:
        """Subscribe to a raw Gate.io channel."""
        await self._native_client.subscribe(channel, payload)

    async def unsubscribe(self, channel: str, payload: list[str]) -> None:
        """Unsubscribe from a raw Gate.io channel."""
        await self._native_client.unsubscribe(channel, payload)

    async def subscribe_ticker(self, product_symbol: str) -> None:
        """Subscribe to ticker events."""
        await self._native_client.subscribe_ticker(product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        """Subscribe to public trade events."""
        await self._native_client.subscribe_trades(product_symbol)

    async def subscribe_candlesticks(self, product_symbol: str, interval: str) -> None:
        """Subscribe to candlestick events."""
        await self._native_client.subscribe_candlesticks(product_symbol, interval)

    async def subscribe_book_ticker(self, product_symbol: str) -> None:
        """Subscribe to best bid/ask events."""
        await self._native_client.subscribe_book_ticker(product_symbol)

    async def subscribe_orderbook(self, product_symbol: str, speed: str = "100ms") -> None:
        """Subscribe to incremental order book updates."""
        await self._native_client.subscribe_orderbook(product_symbol, speed)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


class PrivateClient(AsyncWebSocketMixin):
    """Async Gate.io private WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a Gate.io private WebSocket client."""
        self._native_client = _native.GateioPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
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
        """Send a ping request."""
        await self._native_client.ping()

    async def subscribe(self, channel: str, payload: list[str]) -> None:
        """Subscribe to a raw authenticated Gate.io channel."""
        await self._native_client.subscribe(channel, payload)

    async def unsubscribe(self, channel: str, payload: list[str]) -> None:
        """Unsubscribe from a raw authenticated Gate.io channel."""
        await self._native_client.unsubscribe(channel, payload)

    async def subscribe_orders(self, product_symbols: list[str]) -> None:
        """Subscribe to order updates."""
        await self._native_client.subscribe_orders(product_symbols)

    async def subscribe_user_trades(self, product_symbols: list[str]) -> None:
        """Subscribe to personal trade updates."""
        await self._native_client.subscribe_user_trades(product_symbols)

    async def subscribe_balances(self) -> None:
        """Subscribe to balance updates."""
        await self._native_client.subscribe_balances()

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async Gate.io public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PrivateClient:
    """Create an async Gate.io private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        timeout=timeout,
        base_url=base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
