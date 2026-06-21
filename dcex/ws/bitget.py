"""Bitget async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Bitget public market WebSocket client."""

    def __init__(
        self,
        inst_type: str = "SPOT",
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a Bitget public WebSocket client."""
        self._native_client = _native.BitgetPublicWebSocketClient(
            inst_type=inst_type,
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

    async def subscribe_channel(self, channel: str, product_symbol: str) -> None:
        """Subscribe to a Bitget public channel."""
        await self._native_client.subscribe_channel(channel, product_symbol)

    async def unsubscribe_channel(self, channel: str, product_symbol: str) -> None:
        """Unsubscribe from a Bitget public channel."""
        await self._native_client.unsubscribe_channel(channel, product_symbol)

    async def subscribe_ticker(self, product_symbol: str) -> None:
        """Subscribe to ticker events for a product."""
        await self._native_client.subscribe_ticker(product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        """Subscribe to trade events for a product."""
        await self._native_client.subscribe_trades(product_symbol)

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 5) -> None:
        """Subscribe to order book events for a product."""
        await self._native_client.subscribe_orderbook(product_symbol, depth)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        """Subscribe to kline events for a product."""
        await self._native_client.subscribe_klines(product_symbol, interval)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Bitget WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Bitget private WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a Bitget private WebSocket client."""
        self._native_client = _native.BitgetPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection and login."""
        await self._native_client.connect()

    async def login(self) -> None:
        """Send the Bitget login operation."""
        await self._native_client.login()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send an application-level ping."""
        await self._native_client.ping()

    async def subscribe_channel(
        self,
        inst_type: str,
        channel: str,
        inst_id: str | None = None,
        coin: str | None = None,
    ) -> None:
        """Subscribe to a Bitget private channel."""
        await self._native_client.subscribe_channel(inst_type, channel, inst_id, coin)

    async def unsubscribe_channel(
        self,
        inst_type: str,
        channel: str,
        inst_id: str | None = None,
        coin: str | None = None,
    ) -> None:
        """Unsubscribe from a Bitget private channel."""
        await self._native_client.unsubscribe_channel(inst_type, channel, inst_id, coin)

    async def subscribe_orders(
        self,
        inst_type: str = "USDT-FUTURES",
        inst_id: str | None = None,
    ) -> None:
        """Subscribe to order update events."""
        await self._native_client.subscribe_orders(inst_type, inst_id)

    async def subscribe_fills(
        self,
        inst_type: str = "USDT-FUTURES",
        inst_id: str | None = None,
    ) -> None:
        """Subscribe to fill update events."""
        await self._native_client.subscribe_fills(inst_type, inst_id)

    async def subscribe_positions(
        self,
        inst_type: str = "USDT-FUTURES",
        inst_id: str | None = None,
    ) -> None:
        """Subscribe to position update events."""
        await self._native_client.subscribe_positions(inst_type, inst_id)

    async def subscribe_account(
        self,
        inst_type: str = "USDT-FUTURES",
        coin: str | None = None,
    ) -> None:
        """Subscribe to account balance events."""
        await self._native_client.subscribe_account(inst_type, coin)

    async def subscribe_equity(self, inst_type: str = "USDT-FUTURES") -> None:
        """Subscribe to equity update events."""
        await self._native_client.subscribe_equity(inst_type)

    def is_logged_in(self) -> bool:
        """Return whether login has been acknowledged."""
        return bool(self._native_client.is_logged_in())

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Bitget WebSocket event payload: {event!r}")


def public(
    inst_type: str = "SPOT",
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PublicClient:
    """Create an async Bitget public market WebSocket client."""
    return PublicClient(inst_type=inst_type, timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    passphrase: str,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PrivateClient:
    """Create an async Bitget private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        timeout=timeout,
        base_url=base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
