"""Arcus market and address-scoped WebSocket subscriptions."""

import json
import os
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin


class PublicClient(AsyncWebSocketMixin):
    """Read-only Arcus WebSocket channels on one multiplexed connection."""

    def __init__(self, *, testnet: bool = False, timeout: float = 10.0) -> None:
        self._native_client = load_native().ArcusWebSocketClient(testnet=testnet, timeout=timeout)

    def is_connected(self) -> bool:
        """Return whether the socket is connected."""
        return bool(self._native_client.is_connected())

    async def connect(self) -> None:
        """Open the socket."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the socket."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send a WebSocket ping."""
        await self._native_client.ping()

    async def subscribe(self, channel: str, id: str | None = None) -> None:
        """Subscribe to a market/global or address-scoped channel."""
        await self._native_client.subscribe(channel, id)

    async def unsubscribe(self, channel: str, id: str | None = None) -> None:
        """Remove a channel subscription."""
        await self._native_client.unsubscribe(channel, id)

    async def subscribe_bbo(self, market: str) -> None:
        """Subscribe to best-bid/offer updates for a display-name market."""
        await self.subscribe("bbo", market)

    async def subscribe_orderbook(self, market: str) -> None:
        """Subscribe to L2 order-book snapshots."""
        await self.subscribe("l2Orderbook", market)

    async def subscribe_trades(self, market: str) -> None:
        """Subscribe to public market trades."""
        await self.subscribe("trades", market)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode a WebSocket event."""
        event = json.loads(await self._native_client.recv())
        if isinstance(event, dict | list):
            return event
        raise RuntimeError("Unexpected Arcus WebSocket event payload.")


class PrivateClient(PublicClient):
    """Address-scoped order/account streams; Arcus makes these publicly readable."""

    def __init__(
        self, address: str | None = None, *, testnet: bool = False, timeout: float = 10.0
    ) -> None:
        super().__init__(testnet=testnet, timeout=timeout)
        prefix = "ARCUS_TESTNET" if testnet else "ARCUS_MAINNET"
        self.address = address or os.getenv(f"{prefix}_ADDRESS")
        if not self.address:
            raise ValueError("Arcus account WebSocket requires a wallet address.")

    async def subscribe_account(self) -> None:
        """Subscribe to account snapshots and state updates."""
        await self.subscribe("account", self.address)

    async def subscribe_orders(self) -> None:
        """Subscribe to order acknowledgements and terminal state."""
        await self.subscribe("orders", self.address)

    async def subscribe_fills(self) -> None:
        """Subscribe to account fills."""
        await self.subscribe("userFills", self.address)

    async def subscribe_positions(self) -> None:
        """Subscribe to open position updates."""
        await self.subscribe("positions", self.address)


def public(*, testnet: bool = False, timeout: float = 10.0) -> PublicClient:
    """Create an Arcus market WebSocket client."""
    return PublicClient(testnet=testnet, timeout=timeout)


def private(
    address: str | None = None, *, testnet: bool = False, timeout: float = 10.0
) -> PrivateClient:
    """Create an Arcus address-scoped WebSocket client."""
    return PrivateClient(address=address, testnet=testnet, timeout=timeout)


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
