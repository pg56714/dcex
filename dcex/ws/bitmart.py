"""BitMart async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


def _decode_event(body: bytes | bytearray | memoryview) -> dict[str, Any] | list[Any] | str:
    event = json.loads(bytes(body))
    if isinstance(event, dict | list | str):
        return event
    raise RuntimeError(f"Unexpected BitMart WebSocket event payload: {event!r}")


class PublicClient(AsyncWebSocketMixin):
    """Async BitMart public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a BitMart public WebSocket client."""
        self._native_client = _native.BitmartPublicWebSocketClient(
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
        """Send an application-level ping."""
        await self._native_client.ping()

    async def subscribe(self, topics: list[str]) -> None:
        """Subscribe to raw BitMart topics."""
        await self._native_client.subscribe(topics)

    async def unsubscribe(self, topics: list[str]) -> None:
        """Unsubscribe from raw BitMart topics."""
        await self._native_client.unsubscribe(topics)

    async def request_depth_snapshot(self, product_symbol: str) -> None:
        """Request a one-shot incremental-depth snapshot."""
        await self._native_client.request_depth_snapshot(product_symbol)

    async def subscribe_ticker(self, product_symbol: str) -> None:
        """Subscribe to ticker events for a product."""
        await self._native_client.subscribe_ticker(product_symbol)

    async def subscribe_book_ticker(self, product_symbol: str) -> None:
        """Subscribe to best bid/ask events for a product."""
        await self._native_client.subscribe_book_ticker(product_symbol)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        """Subscribe to kline events for a product."""
        await self._native_client.subscribe_klines(product_symbol, interval)

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 20) -> None:
        """Subscribe to order book events for a product."""
        await self._native_client.subscribe_orderbook(product_symbol, depth)

    async def subscribe_depth_increase(self, product_symbol: str) -> None:
        """Subscribe to incremental depth events for a product."""
        await self._native_client.subscribe_depth_increase(product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        """Subscribe to trade events for a product."""
        await self._native_client.subscribe_trades(product_symbol)

    async def recv(self) -> dict[str, Any] | list[Any] | str:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


class PrivateClient(AsyncWebSocketMixin):
    """Async BitMart private WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        memo: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a BitMart private WebSocket client."""
        self._native_client = _native.BitmartPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            memo=memo,
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection and login."""
        await self._native_client.connect()

    async def login(self) -> None:
        """Send the BitMart login operation."""
        await self._native_client.login()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send an application-level ping."""
        await self._native_client.ping()

    async def subscribe(self, topics: list[str]) -> None:
        """Subscribe to raw BitMart private topics."""
        await self._native_client.subscribe(topics)

    async def unsubscribe(self, topics: list[str]) -> None:
        """Unsubscribe from raw BitMart private topics."""
        await self._native_client.unsubscribe(topics)

    async def subscribe_orders(self, product_symbol: str | None = None) -> None:
        """Subscribe to order update events."""
        await self._native_client.subscribe_orders(product_symbol)

    async def subscribe_balance(self) -> None:
        """Subscribe to balance change events."""
        await self._native_client.subscribe_balance()

    def is_logged_in(self) -> bool:
        """Return whether login has been sent."""
        return bool(self._native_client.is_logged_in())

    async def recv(self) -> dict[str, Any] | list[Any] | str:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async BitMart public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    memo: str,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PrivateClient:
    """Create an async BitMart private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        memo=memo,
        timeout=timeout,
        base_url=base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
