"""KuCoin async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


def _decode_event(body: bytes | bytearray | memoryview) -> dict[str, Any] | list[Any]:
    event = json.loads(bytes(body))
    if isinstance(event, dict | list):
        return event
    raise RuntimeError(f"Unexpected KuCoin WebSocket event payload: {event!r}")


class PublicClient(AsyncWebSocketMixin):
    """Async KuCoin Spot or Futures public market WebSocket client."""

    def __init__(
        self,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        market: str = "spot",
    ) -> None:
        """Create a KuCoin public WebSocket client."""
        self._native_client = _native.KucoinPublicWebSocketClient(
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            futures_http_base_url=futures_http_base_url,
            market=market,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> str:
        """Send an application-level ping."""
        return str(await self._native_client.ping())

    async def subscribe(self, topic: str) -> str:
        """Subscribe to a raw KuCoin topic."""
        return str(await self._native_client.subscribe(topic))

    async def unsubscribe(self, topic: str) -> str:
        """Unsubscribe from a raw KuCoin topic."""
        return str(await self._native_client.unsubscribe(topic))

    async def subscribe_ticker(self, product_symbol: str) -> str:
        """Subscribe to ticker events."""
        return str(await self._native_client.subscribe_ticker(product_symbol))

    async def subscribe_trades(self, product_symbol: str) -> str:
        """Subscribe to public trade events."""
        return str(await self._native_client.subscribe_trades(product_symbol))

    async def subscribe_orderbook(self, product_symbol: str) -> str:
        """Subscribe to level2 order book updates."""
        return str(await self._native_client.subscribe_orderbook(product_symbol))

    async def subscribe_klines(self, product_symbol: str, interval: str) -> str:
        """Subscribe to kline events."""
        return str(await self._native_client.subscribe_klines(product_symbol, interval))

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


class PrivateClient(AsyncWebSocketMixin):
    """Async KuCoin Spot or Futures private WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        market: str = "spot",
    ) -> None:
        """Create a KuCoin private WebSocket client."""
        self._native_client = _native.KucoinPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            futures_http_base_url=futures_http_base_url,
            market=market,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> str:
        """Send an application-level ping."""
        return str(await self._native_client.ping())

    async def subscribe(self, topic: str) -> str:
        """Subscribe to a raw authenticated KuCoin topic."""
        return str(await self._native_client.subscribe(topic))

    async def unsubscribe(self, topic: str) -> str:
        """Unsubscribe from a raw authenticated KuCoin topic."""
        return str(await self._native_client.unsubscribe(topic))

    async def subscribe_orders(self) -> str:
        """Subscribe to order update events."""
        return str(await self._native_client.subscribe_orders())

    async def subscribe_balances(self) -> str:
        """Subscribe to balance update events."""
        return str(await self._native_client.subscribe_balances())

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        return _decode_event(await self._native_client.recv())


def public(
    timeout: float = 10.0,
    spot_http_base_url: str | None = None,
    futures_http_base_url: str | None = None,
    market: str = "spot",
) -> PublicClient:
    """Create an async KuCoin Spot or Futures public market WebSocket client."""
    return PublicClient(
        timeout=timeout,
        spot_http_base_url=spot_http_base_url,
        futures_http_base_url=futures_http_base_url,
        market=market,
    )


def private(
    api_key: str,
    api_secret: str,
    passphrase: str,
    timeout: float = 10.0,
    spot_http_base_url: str | None = None,
    futures_http_base_url: str | None = None,
    market: str = "spot",
) -> PrivateClient:
    """Create an async KuCoin Spot or Futures private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        timeout=timeout,
        spot_http_base_url=spot_http_base_url,
        futures_http_base_url=futures_http_base_url,
        market=market,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
