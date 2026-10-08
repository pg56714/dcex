"""Ondo perpetual and public spot WebSocket clients backed by the Rust core."""

# ruff: noqa: D102, D103

import json
import os
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin


def _decode_event(body: bytes | bytearray | memoryview) -> dict[str, Any] | list[Any]:
    event = json.loads(bytes(body))
    if isinstance(event, dict | list):
        return event
    raise RuntimeError(f"Unexpected Ondo WebSocket event payload: {event!r}")


def _markets(markets: str | list[str] | None) -> list[str]:
    if markets is None:
        return []
    return [markets] if isinstance(markets, str) else markets


class PublicClient(AsyncWebSocketMixin):
    """Ondo public market streams on one multiplexed connection."""

    def set_product_table(self, table: Any) -> None:  # noqa: ANN401
        """Use exact canonical/native symbols from a native ProductTable."""
        self._native_client.set_product_table(table)

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self._native_client = load_native().OndoPublicWebSocketClient(
            timeout=timeout,
            base_url=base_url,
        )

    def is_connected(self) -> bool:
        return bool(self._native_client.is_connected())

    async def connect(self) -> None:
        await self._native_client.connect()

    async def close(self) -> None:
        await self._native_client.close()

    async def ping(self) -> None:
        await self._native_client.ping()

    async def subscribe(self, channel: str, markets: str | list[str] | None = None) -> None:
        await self._native_client.subscribe(channel, _markets(markets))

    async def unsubscribe(self, channel: str, markets: str | list[str] | None = None) -> None:
        await self._native_client.unsubscribe(channel, _markets(markets))

    async def subscribe_trades(self, markets: str | list[str]) -> None:
        await self.subscribe("tradesPerps", markets)

    async def subscribe_top_of_book(self, markets: str | list[str]) -> None:
        await self.subscribe("topOfBooksPerps", markets)

    async def subscribe_depth(self, markets: str | list[str]) -> None:
        await self.subscribe("depthBooksPerps", markets)

    async def subscribe_spot_top_of_book(self, markets: str | list[str]) -> None:
        await self.subscribe("topOfBooksSpot", markets)

    async def subscribe_spot_depth(self, markets: str | list[str]) -> None:
        await self.subscribe("depthBooksSpot", markets)

    async def subscribe_spot_trades(self, markets: str | list[str]) -> None:
        await self.subscribe("tradesSpot", markets)

    async def subscribe_mark_prices(self, markets: str | list[str]) -> None:
        await self.subscribe("markPricesPerps", markets)

    async def subscribe_funding_rates(self, markets: str | list[str]) -> None:
        await self.subscribe("fundingRatesPerps", markets)

    async def subscribe_klines(self, market: str, resolution: str) -> None:
        await self._native_client.subscribe_klines(market, resolution)

    async def recv(self) -> dict[str, Any] | list[Any]:
        return _decode_event(await self._native_client.recv())


class PrivateClient(AsyncWebSocketMixin):
    """Ondo authenticated order/account streams."""

    def __init__(
        self,
        api_key_id: str | None = None,
        api_secret: str | None = None,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self._native_client = load_native().OndoPrivateWebSocketClient(
            api_key_id=api_key_id or os.getenv("ONDO_API_KEY_ID") or None,
            api_secret=api_secret or os.getenv("ONDO_API_SECRET") or None,
            timeout=timeout,
            base_url=base_url,
        )

    def is_connected(self) -> bool:
        return bool(self._native_client.is_connected())

    async def connect(self) -> None:
        await self._native_client.connect()

    async def close(self) -> None:
        await self._native_client.close()

    async def ping(self) -> None:
        await self._native_client.ping()

    async def subscribe(self, channel: str, markets: str | list[str] | None = None) -> None:
        await self._native_client.subscribe(channel, _markets(markets))

    async def subscribe_orders(self, markets: str | list[str] | None = None) -> None:
        await self.subscribe("ordersPerps", markets)

    async def subscribe_fills(self, markets: str | list[str] | None = None) -> None:
        await self.subscribe("fillsPerps", markets)

    async def subscribe_positions(self) -> None:
        await self.subscribe("positionsPerps")

    async def subscribe_balance(self) -> None:
        await self.subscribe("balancePerps")

    async def subscribe_cancel_all_orders_after(self, timeout_seconds: int) -> None:
        """Arm or refresh the perps cancel-all deadline in seconds."""
        await self._native_client.subscribe_cancel_all_orders_after(timeout_seconds)

    async def recv(self) -> dict[str, Any] | list[Any]:
        return _decode_event(await self._native_client.recv())


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key_id: str | None = None,
    api_secret: str | None = None,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> PrivateClient:
    return PrivateClient(
        api_key_id=api_key_id,
        api_secret=api_secret,
        timeout=timeout,
        base_url=base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]
