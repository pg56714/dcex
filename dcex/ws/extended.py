"""Extended async WebSocket clients backed by the Rust core."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


def _decode_event(body: bytes | bytearray | memoryview) -> dict[str, Any] | list[Any]:
    event = json.loads(bytes(body))
    if isinstance(event, dict | list):
        return event
    raise RuntimeError(f"Unexpected Extended WebSocket event payload: {event!r}")


class PublicClient(AsyncWebSocketMixin):
    """
    Async Extended public WebSocket client.

    Extended selects a stream in the WebSocket handshake. Each ``subscribe_*``
    call therefore establishes that stream and replaces any existing stream on
    this client instance.
    """

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self._native_client = _native.ExtendedPublicWebSocketClient(
            timeout=timeout,
            base_url=base_url,
        )

    def is_connected(self) -> bool:
        """Return whether a stream is currently connected."""
        return bool(self._native_client.is_connected())

    async def connect(self) -> None:
        """Connect to the all-markets order book stream by default."""
        await self.subscribe_orderbook()

    async def close(self) -> None:
        """Close the active stream, if any."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send a WebSocket ping on the active stream."""
        await self._native_client.ping()

    async def subscribe_orderbook(
        self,
        market: str | None = None,
        depth: int | None = None,
    ) -> None:
        """Connect to the order book stream; ``depth=1`` selects best bid/ask."""
        await self._native_client.subscribe_orderbook(market, depth)

    async def subscribe_trades(self, market: str | None = None) -> None:
        """Connect to the public trades stream."""
        await self._native_client.subscribe_trades(market)

    async def subscribe_funding(self, market: str | None = None) -> None:
        """Connect to the perpetual funding stream."""
        await self._native_client.subscribe_funding(market)

    async def subscribe_candles(
        self,
        market: str,
        candle_type: str,
        interval: str,
    ) -> None:
        """Connect to a candle stream using Extended ISO 8601 intervals."""
        await self._native_client.subscribe_candles(market, candle_type, interval)

    async def subscribe_mark_price(self, market: str | None = None) -> None:
        """Connect to the mark-price stream."""
        await self._native_client.subscribe_mark_price(market)

    async def subscribe_index_price(self, market: str | None = None) -> None:
        """Connect to the index-price stream."""
        await self._native_client.subscribe_index_price(market)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one stream event."""
        return _decode_event(await self._native_client.recv())


class PrivateClient(AsyncWebSocketMixin):
    """Async Extended authenticated account-updates WebSocket client."""

    def __init__(
        self,
        api_key: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self._native_client = _native.ExtendedPrivateWebSocketClient(
            api_key=api_key,
            timeout=timeout,
            base_url=base_url,
        )

    def is_connected(self) -> bool:
        """Return whether the account stream is connected."""
        return bool(self._native_client.is_connected())

    async def connect(self) -> None:
        """Connect to the authenticated account-updates stream."""
        await self._native_client.connect()

    async def subscribe_account(self) -> None:
        """Connect to the account-updates stream if not already connected."""
        await self._native_client.subscribe_account()

    async def close(self) -> None:
        """Close the account-updates stream."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send a WebSocket ping."""
        await self._native_client.ping()

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one account event."""
        return _decode_event(await self._native_client.recv())


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an Extended public WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PrivateClient:
    """Create an Extended authenticated account-updates WebSocket client."""
    return PrivateClient(api_key=api_key, timeout=timeout, base_url=base_url)


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
