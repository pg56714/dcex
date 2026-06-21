"""BitMEX async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


def _decode_event(body: bytes | bytearray | memoryview) -> dict[str, Any] | list[Any]:
    event = json.loads(bytes(body))
    if isinstance(event, dict | list):
        return event
    raise RuntimeError(f"Unexpected BitMEX WebSocket event payload: {event!r}")


class PublicClient(AsyncWebSocketMixin):
    """Async BitMEX public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a BitMEX public WebSocket client."""
        self._native_client = _native.BitmexPublicWebSocketClient(
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
        """Send a ping command."""
        await self._native_client.ping()

    async def subscribe(self, args: list[str]) -> None:
        """Subscribe to raw BitMEX table arguments."""
        await self._native_client.subscribe(args)

    async def unsubscribe(self, args: list[str]) -> None:
        """Unsubscribe from raw BitMEX table arguments."""
        await self._native_client.unsubscribe(args)

    async def subscribe_table(
        self,
        table: str,
        product_symbol: str | None = None,
    ) -> None:
        """Subscribe to a BitMEX table."""
        await self._native_client.subscribe_table(table, product_symbol)

    async def unsubscribe_table(
        self,
        table: str,
        product_symbol: str | None = None,
    ) -> None:
        """Unsubscribe from a BitMEX table."""
        await self._native_client.unsubscribe_table(table, product_symbol)

    async def subscribe_instrument(self, product_symbol: str) -> None:
        """Subscribe to instrument updates."""
        await self._native_client.subscribe_instrument(product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        """Subscribe to trade events."""
        await self._native_client.subscribe_trades(product_symbol)

    async def subscribe_quotes(self, product_symbol: str) -> None:
        """Subscribe to quote events."""
        await self._native_client.subscribe_quotes(product_symbol)

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 10) -> None:
        """Subscribe to order book events."""
        await self._native_client.subscribe_orderbook(product_symbol, depth)

    async def subscribe_klines(self, product_symbol: str, bin_size: str) -> None:
        """Subscribe to trade bin events."""
        await self._native_client.subscribe_klines(product_symbol, bin_size)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


class PrivateClient(AsyncWebSocketMixin):
    """Async BitMEX private WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a BitMEX private WebSocket client."""
        self._native_client = _native.BitmexPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the authenticated WebSocket connection."""
        await self._native_client.connect()

    async def login(self) -> None:
        """Open or mark the authenticated connection."""
        await self._native_client.login()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send a ping command."""
        await self._native_client.ping()

    async def subscribe(self, args: list[str]) -> None:
        """Subscribe to raw BitMEX private table arguments."""
        await self._native_client.subscribe(args)

    async def unsubscribe(self, args: list[str]) -> None:
        """Unsubscribe from raw BitMEX private table arguments."""
        await self._native_client.unsubscribe(args)

    async def subscribe_orders(self, product_symbol: str) -> None:
        """Subscribe to order updates."""
        await self._native_client.subscribe_orders(product_symbol)

    async def subscribe_executions(self, product_symbol: str) -> None:
        """Subscribe to execution updates."""
        await self._native_client.subscribe_executions(product_symbol)

    async def subscribe_positions(self, product_symbol: str) -> None:
        """Subscribe to position updates."""
        await self._native_client.subscribe_positions(product_symbol)

    async def subscribe_margin(self) -> None:
        """Subscribe to margin updates."""
        await self._native_client.subscribe_margin()

    async def subscribe_wallet(self) -> None:
        """Subscribe to wallet updates."""
        await self._native_client.subscribe_wallet()

    def is_authenticated(self) -> bool:
        """Return whether the authenticated connection has been opened."""
        return bool(self._native_client.is_authenticated())

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async BitMEX public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PrivateClient:
    """Create an async BitMEX private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        timeout=timeout,
        base_url=base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
