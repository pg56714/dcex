"""Kraken async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Kraken public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a Kraken public WebSocket client."""
        self._native_client = _native.KrakenPublicWebSocketClient(
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> int:
        """Send an application-level ping."""
        return int(await self._native_client.ping())

    async def subscribe_channel(self, channel: str, product_symbols: list[str]) -> int:
        """Subscribe to a Kraken public channel."""
        return int(await self._native_client.subscribe_channel(channel, product_symbols))

    async def unsubscribe_channel(self, channel: str, product_symbols: list[str]) -> int:
        """Unsubscribe from a Kraken public channel."""
        return int(await self._native_client.unsubscribe_channel(channel, product_symbols))

    async def subscribe_ticker(self, product_symbol: str) -> int:
        """Subscribe to ticker events for a product."""
        return int(await self._native_client.subscribe_ticker(product_symbol))

    async def subscribe_trades(self, product_symbol: str) -> int:
        """Subscribe to trade events for a product."""
        return int(await self._native_client.subscribe_trades(product_symbol))

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 10) -> int:
        """Subscribe to order book events for a product."""
        return int(await self._native_client.subscribe_orderbook(product_symbol, depth))

    async def subscribe_klines(self, product_symbol: str, interval: int = 1) -> int:
        """Subscribe to OHLC candle events for a product."""
        return int(await self._native_client.subscribe_klines(product_symbol, interval))

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Kraken WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Kraken private WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        """Create a Kraken private WebSocket client."""
        self._native_client = _native.KrakenPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            ws_base_url=ws_base_url,
        )

    async def connect(self) -> str:
        """Fetch a token and open the WebSocket connection."""
        return str(await self._native_client.connect())

    async def fetch_token(self) -> str:
        """Fetch and store a Kraken WebSocket token."""
        return str(await self._native_client.fetch_token())

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> int:
        """Send an application-level ping."""
        return int(await self._native_client.ping())

    async def subscribe_balances(self) -> int:
        """Subscribe to balance update events."""
        return int(await self._native_client.subscribe_balances())

    async def unsubscribe_balances(self) -> int:
        """Unsubscribe from balance update events."""
        return int(await self._native_client.unsubscribe_balances())

    async def subscribe_executions(
        self,
        snap_orders: bool = True,
        snap_trades: bool = False,
    ) -> int:
        """Subscribe to order status and execution events."""
        return int(await self._native_client.subscribe_executions(snap_orders, snap_trades))

    async def unsubscribe_executions(self) -> int:
        """Unsubscribe from order status and execution events."""
        return int(await self._native_client.unsubscribe_executions())

    def token(self) -> str | None:
        """Return the current WebSocket token if one has been fetched."""
        token = self._native_client.token()
        return str(token) if token is not None else None

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Kraken WebSocket event payload: {event!r}")


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async Kraken public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    timeout: float = 10.0,
    spot_http_base_url: str | None = None,
    ws_base_url: str | None = None,
) -> PrivateClient:
    """Create an async Kraken private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        timeout=timeout,
        spot_http_base_url=spot_http_base_url,
        ws_base_url=ws_base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
