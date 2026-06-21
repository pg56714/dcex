"""Lighter async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Lighter public market WebSocket client."""

    def __init__(
        self,
        testnet: bool = False,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a Lighter public WebSocket client."""
        self._native_client = _native.LighterPublicWebSocketClient(
            testnet=testnet,
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
        """Send a WebSocket ping frame."""
        await self._native_client.ping()

    async def subscribe(self, channel: str) -> None:
        """Subscribe to a raw Lighter channel."""
        await self._native_client.subscribe(channel)

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a raw Lighter channel."""
        await self._native_client.unsubscribe(channel)

    async def subscribe_orderbook(self, market_id: int) -> None:
        """Subscribe to order book updates for a market."""
        await self._native_client.subscribe_orderbook(market_id)

    async def subscribe_ticker(self, market_id: int) -> None:
        """Subscribe to best bid/offer updates for a market."""
        await self._native_client.subscribe_ticker(market_id)

    async def subscribe_market_stats(self, market_id: int) -> None:
        """Subscribe to market stats updates for a market."""
        await self._native_client.subscribe_market_stats(market_id)

    async def subscribe_all_market_stats(self) -> None:
        """Subscribe to market stats updates for all perpetual markets."""
        await self._native_client.subscribe_all_market_stats()

    async def subscribe_trades(self, market_id: int) -> None:
        """Subscribe to trade updates for a market."""
        await self._native_client.subscribe_trades(market_id)

    async def subscribe_klines(self, market_id: int, resolution: str) -> None:
        """Subscribe to candlestick updates for a market."""
        await self._native_client.subscribe_klines(market_id, resolution)

    async def subscribe_mark_price_klines(self, market_id: int, resolution: str) -> None:
        """Subscribe to mark price candlestick updates for a market."""
        await self._native_client.subscribe_mark_price_klines(market_id, resolution)

    async def subscribe_spot_market_stats(self, market_id: int) -> None:
        """Subscribe to spot market stats updates for a market."""
        await self._native_client.subscribe_spot_market_stats(market_id)

    async def subscribe_all_spot_market_stats(self) -> None:
        """Subscribe to spot market stats updates for all spot markets."""
        await self._native_client.subscribe_all_spot_market_stats()

    async def subscribe_height(self) -> None:
        """Subscribe to blockchain height updates."""
        await self._native_client.subscribe_height()

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Lighter WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Lighter private user WebSocket client."""

    def __init__(
        self,
        account_index: int,
        api_key_index: int,
        api_private_key: str,
        testnet: bool = False,
        timeout: float = 10.0,
        ws_base_url: str | None = None,
        http_base_url: str | None = None,
    ) -> None:
        """Create a Lighter private WebSocket client."""
        self._native_client = _native.LighterPrivateWebSocketClient(
            account_index=account_index,
            api_key_index=api_key_index,
            api_private_key=api_private_key,
            testnet=testnet,
            timeout=timeout,
            ws_base_url=ws_base_url,
            http_base_url=http_base_url,
        )

    def account_index(self) -> int:
        """Return the account index."""
        return int(self._native_client.account_index())

    def create_auth_token(
        self,
        deadline: int | None = None,
        api_key_index: int | None = None,
    ) -> str:
        """Create a Lighter auth token."""
        return str(self._native_client.create_auth_token(deadline, api_key_index))

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send a WebSocket ping frame."""
        await self._native_client.ping()

    async def subscribe(self, channel: str, auth: str | None = None) -> None:
        """Subscribe to a raw Lighter channel."""
        await self._native_client.subscribe(channel, auth)

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a raw Lighter channel."""
        await self._native_client.unsubscribe(channel)

    async def subscribe_authenticated(self, channel: str) -> None:
        """Subscribe to a raw Lighter channel with generated auth."""
        await self._native_client.subscribe_authenticated(channel)

    async def subscribe_account_all(self) -> None:
        """Subscribe to account-wide updates."""
        await self._native_client.subscribe_account_all()

    async def subscribe_account_market(self, market_id: int) -> None:
        """Subscribe to authenticated account market updates."""
        await self._native_client.subscribe_account_market(market_id)

    async def subscribe_user_stats(self) -> None:
        """Subscribe to account stats updates."""
        await self._native_client.subscribe_user_stats()

    async def subscribe_account_tx(self) -> None:
        """Subscribe to authenticated account transaction updates."""
        await self._native_client.subscribe_account_tx()

    async def subscribe_account_all_orders(self) -> None:
        """Subscribe to authenticated all-order updates."""
        await self._native_client.subscribe_account_all_orders()

    async def subscribe_pool_data(self) -> None:
        """Subscribe to authenticated pool data updates."""
        await self._native_client.subscribe_pool_data()

    async def subscribe_pool_info(self) -> None:
        """Subscribe to authenticated pool info updates."""
        await self._native_client.subscribe_pool_info()

    async def subscribe_notifications(self) -> None:
        """Subscribe to authenticated notification updates."""
        await self._native_client.subscribe_notifications()

    async def subscribe_account_orders(self, market_id: int) -> None:
        """Subscribe to authenticated account order updates for a market."""
        await self._native_client.subscribe_account_orders(market_id)

    async def subscribe_account_all_trades(self) -> None:
        """Subscribe to account trade updates."""
        await self._native_client.subscribe_account_all_trades()

    async def subscribe_account_all_positions(self) -> None:
        """Subscribe to account position updates."""
        await self._native_client.subscribe_account_all_positions()

    async def subscribe_account_all_assets(self) -> None:
        """Subscribe to authenticated account asset updates."""
        await self._native_client.subscribe_account_all_assets()

    async def subscribe_account_spot_avg_entry_prices(self) -> None:
        """Subscribe to authenticated account spot average entry price updates."""
        await self._native_client.subscribe_account_spot_avg_entry_prices()

    async def subscribe_rfq(self) -> None:
        """Subscribe to authenticated RFQ updates."""
        await self._native_client.subscribe_rfq()

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Lighter WebSocket event payload: {event!r}")


def public(
    testnet: bool = False,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PublicClient:
    """Create an async Lighter public market WebSocket client."""
    return PublicClient(testnet=testnet, timeout=timeout, base_url=base_url)


def private(
    account_index: int,
    api_key_index: int,
    api_private_key: str,
    testnet: bool = False,
    timeout: float = 10.0,
    ws_base_url: str | None = None,
    http_base_url: str | None = None,
) -> PrivateClient:
    """Create an async Lighter private user WebSocket client."""
    return PrivateClient(
        account_index=account_index,
        api_key_index=api_key_index,
        api_private_key=api_private_key,
        testnet=testnet,
        timeout=timeout,
        ws_base_url=ws_base_url,
        http_base_url=http_base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
