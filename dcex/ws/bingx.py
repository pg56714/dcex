"""BingX async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


def _decode_event(body: bytes | bytearray | memoryview) -> dict[str, Any] | list[Any] | str:
    event = json.loads(bytes(body))
    if isinstance(event, dict | list | str):
        return event
    raise RuntimeError(f"Unexpected BingX WebSocket event payload: {event!r}")


class PublicClient(AsyncWebSocketMixin):
    """Async BingX public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a BingX public WebSocket client."""
        self._native_client = _native.BingxPublicWebSocketClient(
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

    async def subscribe(self, data_type: str) -> str:
        """Subscribe to a raw BingX dataType."""
        return str(await self._native_client.subscribe(data_type))

    async def unsubscribe(self, data_type: str) -> str:
        """Unsubscribe from a raw BingX dataType."""
        return str(await self._native_client.unsubscribe(data_type))

    async def subscribe_ticker(self, product_symbol: str) -> str:
        """Subscribe to ticker events."""
        return str(await self._native_client.subscribe_ticker(product_symbol))

    async def subscribe_trades(self, product_symbol: str) -> str:
        """Subscribe to public trade events."""
        return str(await self._native_client.subscribe_trades(product_symbol))

    async def subscribe_orderbook(
        self,
        product_symbol: str,
        depth: int = 5,
        speed: str = "500ms",
    ) -> str:
        """Subscribe to order book events."""
        return str(await self._native_client.subscribe_orderbook(product_symbol, depth, speed))

    async def subscribe_klines(self, product_symbol: str, interval: str) -> str:
        """Subscribe to kline events."""
        return str(await self._native_client.subscribe_klines(product_symbol, interval))

    async def recv(self) -> dict[str, Any] | list[Any] | str:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


class PrivateClient(AsyncWebSocketMixin):
    """Async BingX private WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        """Create a BingX private WebSocket client."""
        self._native_client = _native.BingxPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            http_base_url=http_base_url,
            ws_base_url=ws_base_url,
        )

    async def connect(self) -> str:
        """Open the WebSocket connection and return the listen key."""
        return str(await self._native_client.connect())

    async def connect_with_listen_key(self, listen_key: str) -> None:
        """Open the WebSocket connection with an existing listen key."""
        await self._native_client.connect_with_listen_key(listen_key)

    async def keep_alive(self) -> str:
        """Extend the current listen key."""
        return str(await self._native_client.keep_alive())

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send an application-level ping."""
        await self._native_client.ping()

    async def subscribe(self, data_type: str) -> str:
        """Subscribe to a raw authenticated BingX dataType."""
        return str(await self._native_client.subscribe(data_type))

    async def unsubscribe(self, data_type: str) -> str:
        """Unsubscribe from a raw authenticated BingX dataType."""
        return str(await self._native_client.unsubscribe(data_type))

    async def subscribe_orders(self) -> str:
        """Subscribe to order update events."""
        return str(await self._native_client.subscribe_orders())

    def listen_key(self) -> str | None:
        """Return the active listen key, if one has been created."""
        value = self._native_client.listen_key()
        return str(value) if value is not None else None

    async def recv(self) -> dict[str, Any] | list[Any] | str:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async BingX public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    timeout: float = 10.0,
    http_base_url: str | None = None,
    ws_base_url: str | None = None,
) -> PrivateClient:
    """Create an async BingX private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        timeout=timeout,
        http_base_url=http_base_url,
        ws_base_url=ws_base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
