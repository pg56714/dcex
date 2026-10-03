"""Arcus market/account streams and signed trading RPC."""

import json
import os
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin


class PublicClient(AsyncWebSocketMixin):
    """Read-only Arcus WebSocket channels on one multiplexed connection."""

    def set_product_table(self, table: Any) -> None:  # noqa: ANN401
        """Use exact canonical/native symbols from a native ProductTable."""
        self._native_client.set_product_table(table)

    def __init__(
        self, *, testnet: bool = False, timeout: float = 10.0, base_url: str | None = None
    ) -> None:
        kwargs: dict[str, Any] = {"testnet": testnet, "timeout": timeout}
        if base_url is not None:
            kwargs["base_url"] = base_url
        self._native_client = load_native().ArcusWebSocketClient(**kwargs)

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

    async def get_request(self, request_id: int, method: str, payload: dict[str, Any]) -> None:
        """Send read-only RPC; match the numeric response id returned by recv."""
        await self._native_client.get_request(
            request_id, method, json.dumps(payload, allow_nan=False)
        )

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
        self,
        address: str | None = None,
        *,
        testnet: bool = False,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        super().__init__(testnet=testnet, timeout=timeout, base_url=base_url)
        self.address = address or os.getenv("ARCUS_ADDRESS")
        if not self.address:
            raise ValueError("Arcus account WebSocket requires a wallet address.")

    async def post_request(self, signed_frame: dict[str, Any]) -> None:
        """
        Send a REST client's sign_websocket_request result unchanged.

        Read the 202 acknowledgement with recv, then follow orders/userFills for
        terminal status. Query status before retrying after a timeout.
        """
        address = signed_frame.get("request", {}).get("payload", {}).get("address")
        if (
            not isinstance(address, str)
            or self.address is None
            or address.lower() != self.address.lower()
        ):
            raise ValueError("Signed frame address differs from WebSocket account")
        await self._native_client.post_request(json.dumps(signed_frame, allow_nan=False))

    async def subscribe_settle_loan_results(self) -> None:
        """Subscribe to applied and rejected loan-settlement results."""
        await self.subscribe("settleLoanResults", self.address)

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


def public(
    *, testnet: bool = False, timeout: float = 10.0, base_url: str | None = None
) -> PublicClient:
    """Create an Arcus market WebSocket client."""
    return PublicClient(testnet=testnet, timeout=timeout, base_url=base_url)


def private(
    address: str | None = None,
    *,
    testnet: bool = False,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PrivateClient:
    """Create an Arcus address-scoped WebSocket client."""
    return PrivateClient(address=address, testnet=testnet, timeout=timeout, base_url=base_url)


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
