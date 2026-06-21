"""Aster async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Aster public market WebSocket client."""

    def __init__(
        self,
        market: str = "futures",
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create an Aster public WebSocket client."""
        self._native_client = _native.AsterPublicWebSocketClient(
            market=market,
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def subscribe(self, streams: list[str]) -> int:
        """Subscribe to raw Aster stream names."""
        return int(await self._native_client.subscribe(streams))

    async def unsubscribe(self, streams: list[str]) -> int:
        """Unsubscribe from raw Aster stream names."""
        return int(await self._native_client.unsubscribe(streams))

    async def list_subscriptions(self) -> int:
        """Request the current Aster stream subscription list."""
        return int(await self._native_client.list_subscriptions())

    async def subscribe_trades(self, product_symbol: str) -> int:
        """Subscribe to raw trade events for a product."""
        return int(await self._native_client.subscribe_trades(product_symbol))

    async def subscribe_agg_trades(self, product_symbol: str) -> int:
        """Subscribe to aggregate trade events for a product."""
        return int(await self._native_client.subscribe_agg_trades(product_symbol))

    async def subscribe_orderbook(self, product_symbol: str) -> int:
        """Subscribe to diff order book events for a product."""
        return int(await self._native_client.subscribe_orderbook(product_symbol))

    async def subscribe_book_ticker(self, product_symbol: str) -> int:
        """Subscribe to best bid and ask events for a product."""
        return int(await self._native_client.subscribe_book_ticker(product_symbol))

    async def subscribe_ticker(self, product_symbol: str) -> int:
        """Subscribe to ticker events for a product."""
        return int(await self._native_client.subscribe_ticker(product_symbol))

    async def subscribe_klines(self, product_symbol: str, interval: str) -> int:
        """Subscribe to kline events for a product."""
        return int(await self._native_client.subscribe_klines(product_symbol, interval))

    async def subscribe_mark_price(
        self,
        product_symbol: str,
        fast: bool = False,
    ) -> int:
        """Subscribe to futures mark-price events for a product."""
        return int(await self._native_client.subscribe_mark_price(product_symbol, fast))

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Aster WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Aster private user data WebSocket client."""

    def __init__(
        self,
        signer_address: str,
        private_key: str,
        user_address: str | None = None,
        market: str = "futures",
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        """Create an Aster private WebSocket client."""
        self._native_client = _native.AsterPrivateWebSocketClient(
            signer_address=signer_address,
            private_key=private_key,
            user_address=user_address,
            market=market,
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            futures_http_base_url=futures_http_base_url,
            ws_base_url=ws_base_url,
        )

    async def connect(self) -> str:
        """Open the WebSocket connection and return the listen key."""
        return str(await self._native_client.connect())

    async def connect_with_listen_key(self, listen_key: str) -> None:
        """Open the WebSocket connection with an existing listen key."""
        await self._native_client.connect_with_listen_key(listen_key)

    async def close(self) -> None:
        """Close the WebSocket connection and invalidate the listen key."""
        await self._native_client.close()

    async def keep_alive(self) -> None:
        """Extend the current listen key validity."""
        await self._native_client.keep_alive()

    async def close_listen_key(self) -> None:
        """Invalidate the current listen key."""
        await self._native_client.close_listen_key()

    def listen_key(self) -> str | None:
        """Return the current listen key if connected."""
        value = self._native_client.listen_key()
        return str(value) if value is not None else None

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Aster WebSocket event payload: {event!r}")


def public(
    market: str = "futures",
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PublicClient:
    """Create an async Aster public market WebSocket client."""
    return PublicClient(market=market, timeout=timeout, base_url=base_url)


def private(
    signer_address: str,
    private_key: str,
    user_address: str | None = None,
    market: str = "futures",
    timeout: float = 10.0,
    spot_http_base_url: str | None = None,
    futures_http_base_url: str | None = None,
    ws_base_url: str | None = None,
) -> PrivateClient:
    """Create an async Aster private user data WebSocket client."""
    return PrivateClient(
        signer_address=signer_address,
        private_key=private_key,
        user_address=user_address,
        market=market,
        timeout=timeout,
        spot_http_base_url=spot_http_base_url,
        futures_http_base_url=futures_http_base_url,
        ws_base_url=ws_base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
