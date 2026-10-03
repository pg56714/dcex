"""Hyperliquid async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ._base import AsyncWebSocketMixin

_native = load_native()


def _subscription_bytes(subscription: dict[str, Any]) -> bytes:
    return json.dumps(subscription, separators=(",", ":")).encode()


class PublicClient(AsyncWebSocketMixin):
    """Async Hyperliquid public market WebSocket client."""

    def set_product_table(self, table: Any) -> None:  # noqa: ANN401
        """Use exact canonical/native symbols from a native ProductTable."""
        self._native_client.set_product_table(table)

    def __init__(
        self,
        testnet: bool = False,
        timeout: float = 10.0,
        base_url: str | None = None,
        preload_product_table: bool = False,
    ) -> None:
        """Create a Hyperliquid public WebSocket client."""
        self._native_client = _native.HyperliquidPublicWebSocketClient(
            testnet=testnet,
            timeout=timeout,
            base_url=base_url,
        )
        if preload_product_table:
            table = ProductTableManager.get_instance(Common.HYPERLIQUID)
            self._native_client.set_product_table(table._native_table)

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def post_info(self, request_id: int, payload: dict[str, Any]) -> None:
        """Send an info request; read the response with recv and match its id."""
        await self._native_client.post_info(request_id, json.dumps(payload, allow_nan=False))

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def subscribe(self, subscription: dict[str, Any]) -> None:
        """Subscribe to a raw Hyperliquid subscription object."""
        await self._native_client.subscribe(_subscription_bytes(subscription))

    async def unsubscribe(self, subscription: dict[str, Any]) -> None:
        """Unsubscribe from a raw Hyperliquid subscription object."""
        await self._native_client.unsubscribe(_subscription_bytes(subscription))

    async def subscribe_all_mids(self, dex: str | None = None) -> None:
        """Subscribe to all mids events."""
        await self._native_client.subscribe_all_mids(dex)

    async def subscribe_trades(self, product_symbol: str) -> None:
        """Subscribe to trade events for a product."""
        await self._native_client.subscribe_trades(product_symbol)

    async def subscribe_orderbook(self, product_symbol: str) -> None:
        """Subscribe to L2 order book events for a product."""
        await self._native_client.subscribe_orderbook(product_symbol)

    async def subscribe_l2_book(
        self,
        product_symbol: str,
        n_sig_figs: int | None = None,
        mantissa: int | None = None,
    ) -> None:
        """Subscribe to L2 order book events with optional precision parameters."""
        await self._native_client.subscribe_l2_book(
            product_symbol,
            n_sig_figs,
            mantissa,
        )

    async def subscribe_bbo(self, product_symbol: str) -> None:
        """Subscribe to best bid/offer events for a product."""
        await self._native_client.subscribe_bbo(product_symbol)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        """Subscribe to candle events for a product."""
        await self._native_client.subscribe_klines(product_symbol, interval)

    async def subscribe_active_asset_ctx(self, product_symbol: str) -> None:
        """Subscribe to active asset context events for a product."""
        await self._native_client.subscribe_active_asset_ctx(product_symbol)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Hyperliquid WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Hyperliquid private user WebSocket client."""

    def __init__(
        self,
        user: str,
        testnet: bool = False,
        timeout: float = 10.0,
        base_url: str | None = None,
        preload_product_table: bool = False,
    ) -> None:
        """Create a Hyperliquid private WebSocket client."""
        self._testnet = testnet
        self._native_client = _native.HyperliquidPrivateWebSocketClient(
            user=user,
            testnet=testnet,
            timeout=timeout,
            base_url=base_url,
        )
        if preload_product_table:
            table = ProductTableManager.get_instance(Common.HYPERLIQUID)
            self._native_client.set_product_table(table._native_table)

    def user(self) -> str:
        """Return the normalized user address."""
        return str(self._native_client.user())

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def post_info(self, request_id: int, payload: dict[str, Any]) -> None:
        """Send an info request; read the response with recv and match its id."""
        await self._native_client.post_info(request_id, json.dumps(payload, allow_nan=False))

    def sign_order(
        self,
        orders: list[dict[str, Any]],
        *,
        nonce: int,
        private_key: str,
        grouping: str = "na",
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> dict[str, Any]:
        """
        Sign wire-format orders offline for post_action on this client's network.

        Prices and sizes must be decimal strings. Supply a unique millisecond nonce;
        the returned envelope is signed but has not been submitted.
        """
        return json.loads(
            self._native_client.sign_order(
                json.dumps(orders, allow_nan=False),
                grouping,
                nonce,
                private_key,
                self._testnet,
                vault_address,
                expires_after,
            )
        )

    def sign_cancel(
        self,
        cancels: list[dict[str, int]],
        *,
        nonce: int,
        private_key: str,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> dict[str, Any]:
        """
        Sign {a: asset_id, o: order_id} cancellations offline for post_action.

        Supply a unique millisecond nonce. This method sends no request.
        """
        return json.loads(
            self._native_client.sign_cancel(
                json.dumps(cancels, allow_nan=False),
                nonce,
                private_key,
                self._testnet,
                vault_address,
                expires_after,
            )
        )

    async def post_action(self, request_id: int, payload: dict[str, Any]) -> None:
        """
        Send a signed action unchanged; read the post response with recv.

        Sign the complete payload for the correct network before calling. Use a
        unique request ID. On timeout, query status before retrying.
        """
        await self._native_client.post_action(request_id, json.dumps(payload, allow_nan=False))

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def subscribe(self, subscription: dict[str, Any]) -> None:
        """Subscribe to a raw Hyperliquid subscription object."""
        await self._native_client.subscribe(_subscription_bytes(subscription))

    async def unsubscribe(self, subscription: dict[str, Any]) -> None:
        """Unsubscribe from a raw Hyperliquid subscription object."""
        await self._native_client.unsubscribe(_subscription_bytes(subscription))

    async def subscribe_user_subscription(
        self,
        subscription_type: str,
        dex: str | None = None,
    ) -> None:
        """Subscribe to a user-address scoped Hyperliquid subscription."""
        await self._native_client.subscribe_user_subscription(subscription_type, dex)

    async def unsubscribe_user_subscription(
        self,
        subscription_type: str,
        dex: str | None = None,
    ) -> None:
        """Unsubscribe from a user-address scoped Hyperliquid subscription."""
        await self._native_client.unsubscribe_user_subscription(subscription_type, dex)

    async def subscribe_notifications(self) -> None:
        """Subscribe to notification events."""
        await self._native_client.subscribe_notifications()

    async def subscribe_web_data3(self) -> None:
        """Subscribe to webData3 events."""
        await self._native_client.subscribe_web_data3()

    async def subscribe_clearinghouse_state(self, dex: str | None = None) -> None:
        """Subscribe to clearinghouse state events."""
        await self._native_client.subscribe_clearinghouse_state(dex)

    async def subscribe_open_orders(self, dex: str | None = None) -> None:
        """Subscribe to open order events."""
        await self._native_client.subscribe_open_orders(dex)

    async def subscribe_order_updates(self) -> None:
        """Subscribe to order update events."""
        await self._native_client.subscribe_order_updates()

    async def subscribe_user_events(self) -> None:
        """Subscribe to user event updates."""
        await self._native_client.subscribe_user_events()

    async def subscribe_user_fills(self, aggregate_by_time: bool | None = None) -> None:
        """Subscribe to user fill events."""
        await self._native_client.subscribe_user_fills(aggregate_by_time)

    async def subscribe_user_fundings(self) -> None:
        """Subscribe to user funding events."""
        await self._native_client.subscribe_user_fundings()

    async def subscribe_user_non_funding_ledger_updates(self) -> None:
        """Subscribe to non-funding ledger updates."""
        await self._native_client.subscribe_user_non_funding_ledger_updates()

    async def subscribe_twap_states(self, dex: str | None = None) -> None:
        """Subscribe to TWAP state events."""
        await self._native_client.subscribe_twap_states(dex)

    async def subscribe_user_twap_slice_fills(self) -> None:
        """Subscribe to user TWAP slice fills."""
        await self._native_client.subscribe_user_twap_slice_fills()

    async def subscribe_user_twap_history(self) -> None:
        """Subscribe to user TWAP history."""
        await self._native_client.subscribe_user_twap_history()

    async def subscribe_active_asset_data(self, product_symbol: str) -> None:
        """Subscribe to active asset data for this user."""
        await self._native_client.subscribe_active_asset_data(product_symbol)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Hyperliquid WebSocket event payload: {event!r}")


def public(
    testnet: bool = False,
    timeout: float = 10.0,
    base_url: str | None = None,
    preload_product_table: bool = False,
) -> PublicClient:
    """Create an async Hyperliquid public market WebSocket client."""
    return PublicClient(
        testnet=testnet,
        timeout=timeout,
        base_url=base_url,
        preload_product_table=preload_product_table,
    )


def private(
    user: str,
    testnet: bool = False,
    timeout: float = 10.0,
    base_url: str | None = None,
    preload_product_table: bool = False,
) -> PrivateClient:
    """Create an async Hyperliquid private user WebSocket client."""
    return PrivateClient(
        user=user,
        testnet=testnet,
        timeout=timeout,
        base_url=base_url,
        preload_product_table=preload_product_table,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
