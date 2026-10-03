"""Bitget async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()

UTA_PUBLIC_WS_URL = "wss://ws.bitget.com/v3/ws/public"
UTA_PRIVATE_WS_URL = "wss://ws.bitget.com/v3/ws/private"


class PublicClient(AsyncWebSocketMixin):
    """Async Bitget public market WebSocket client."""

    def set_product_table(self, table: Any) -> None:  # noqa: ANN401
        """Use exact canonical/native symbols from a native ProductTable."""
        self._native_client.set_product_table(table)

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

    async def recv_bytes(self) -> bytes:
        """
        Receive the unmodified text/binary payload, including SBE market frames.

        SBE decoding is the caller's responsibility; use the official schema.
        Subscription acknowledgements and pong remain text payloads.
        """
        return bytes(await self._native_client.recv())

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Bitget WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """
    Async Bitget private WebSocket client.

    The default UTA V3 endpoint uses ``inst_type=UTA``; the
    order/fill/position/account helpers send ``{"instType": "UTA", "topic": ...}``
    subscriptions that cover every product type.
    """

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

    async def trade_request(
        self,
        request_id: str,
        topic: str,
        args: list[dict[str, Any]],
        *,
        category: str | None = None,
        request_time: int | None = None,
    ) -> None:
        """
        Send a UTA trade frame; read the ACK and every per-order result with recv.

        Symbols and argument keys follow the official exchange schema. Decimal
        quantities/prices are strings. Request IDs must be unique among pending
        requests. A successful ACK does not confirm execution. On timeout, query
        order status before retrying to avoid duplicate orders.
        """
        await self._native_client.trade_request(
            request_id, topic, json.dumps(args, allow_nan=False), category, request_time
        )

    async def place_order(
        self,
        request_id: str,
        order: dict[str, Any],
        *,
        category: str | None = None,
        request_time: int | None = None,
    ) -> None:
        """Send UTA place-order; receive the acknowledgement with recv."""
        await self.trade_request(
            request_id, "place-order", [order], category=category, request_time=request_time
        )

    async def modify_order(
        self, request_id: str, order: dict[str, Any], *, category: str | None = None
    ) -> None:
        """Send UTA modify-order; receive the acknowledgement with recv."""
        await self.trade_request(request_id, "modify-order", [order], category=category)

    async def cancel_order(
        self, request_id: str, order: dict[str, Any], *, category: str | None = None
    ) -> None:
        """Send UTA cancel-order; receive the acknowledgement with recv."""
        await self.trade_request(request_id, "cancel-order", [order], category=category)

    async def place_batch_orders(
        self, request_id: str, orders: list[dict[str, Any]], *, category: str | None = None
    ) -> None:
        """Send UTA batch-place; receive the acknowledgement with recv."""
        await self.trade_request(request_id, "batch-place", orders, category=category)

    async def modify_batch_orders(
        self, request_id: str, orders: list[dict[str, Any]], *, category: str | None = None
    ) -> None:
        """Send UTA batch-modify; receive the acknowledgement with recv."""
        await self.trade_request(request_id, "batch-modify", orders, category=category)

    async def cancel_batch_orders(self, request_id: str, orders: list[dict[str, Any]]) -> None:
        """Send UTA batch-cancel; receive the acknowledgement with recv."""
        await self.trade_request(request_id, "batch-cancel", orders)

    async def subscribe_channel(
        self,
        inst_type: str,
        channel: str,
        inst_id: str | None = None,
        coin: str | None = None,
    ) -> None:
        """Subscribe to a private channel; MARGIN/positions-history require a V2 base_url."""
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

    async def subscribe_orders(self) -> None:
        """Subscribe to order update events."""
        await self._native_client.subscribe_orders()

    async def subscribe_fills(self) -> None:
        """Subscribe to fill update events."""
        await self._native_client.subscribe_fills()

    async def subscribe_positions(self) -> None:
        """Subscribe to position update events."""
        await self._native_client.subscribe_positions()

    async def subscribe_account(self) -> None:
        """Subscribe to account balance events."""
        await self._native_client.subscribe_account()

    async def subscribe_equity(self, inst_type: str | None = None) -> None:
        """Subscribe to equity events; requires a V2 private WebSocket base_url."""
        await self._native_client.subscribe_equity(inst_type)

    async def subscribe_reality_orderbook(self, symbol: str) -> None:
        """Subscribe to a whitelisted Reality orderbook on UTA V3 private WS."""
        await self._native_client.subscribe_reality_orderbook(symbol)

    async def unsubscribe_reality_orderbook(self, symbol: str) -> None:
        """Unsubscribe from a Reality orderbook on UTA V3 private WS."""
        await self._native_client.unsubscribe_reality_orderbook(symbol)

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


def uta_public(
    inst_type: str = "SPOT",
    timeout: float = 10.0,
) -> PublicClient:
    """Create an async Bitget UTA V3 public WebSocket client (``topic``/``symbol`` args)."""
    return PublicClient(inst_type=inst_type, timeout=timeout, base_url=UTA_PUBLIC_WS_URL)


def uta_private(
    api_key: str,
    api_secret: str,
    passphrase: str,
    timeout: float = 10.0,
) -> PrivateClient:
    """Create an async Bitget UTA V3 private WebSocket client (``instType=UTA`` topics)."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        timeout=timeout,
        base_url=UTA_PRIVATE_WS_URL,
    )


def reality_private(
    api_key: str,
    api_secret: str,
    passphrase: str,
    timeout: float = 10.0,
) -> PrivateClient:
    """Create an authenticated UTA V3 WebSocket for Reality orderbook data."""
    return PrivateClient(
        api_key,
        api_secret,
        passphrase,
        timeout,
        UTA_PRIVATE_WS_URL,
    )


__all__ = [
    "PrivateClient",
    "PublicClient",
    "private",
    "public",
    "reality_private",
    "uta_private",
    "uta_public",
]


def sbe_public(
    inst_type: str = "usdt-futures",
    *,
    timeout: float = 10.0,
    base_url: str = "wss://ws.bitget.com/v3/ws/public/sbe",
) -> PublicClient:
    """Connect to SBE; subscribe to books1/books50/publicTrade and use recv_bytes."""
    return PublicClient(inst_type=inst_type, timeout=timeout, base_url=base_url)
