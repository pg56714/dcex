"""MEXC async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


def _decode_event(body: bytes | bytearray | memoryview) -> dict[str, Any] | list[Any] | bytes:
    payload = bytes(body)
    try:
        event = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return payload
    if isinstance(event, dict | list):
        return event
    raise RuntimeError(f"Unexpected MEXC WebSocket event payload: {event!r}")


class PublicClient(AsyncWebSocketMixin):
    """Async MEXC public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a MEXC public WebSocket client."""
        self._native_client = _native.MexcPublicWebSocketClient(
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

    async def subscribe(self, channels: list[str]) -> None:
        """Subscribe to raw MEXC channels."""
        await self._native_client.subscribe(channels)

    async def unsubscribe(self, channels: list[str]) -> None:
        """Unsubscribe from raw MEXC channels."""
        await self._native_client.unsubscribe(channels)

    async def subscribe_trades(self, product_symbol: str, speed: str = "100ms") -> None:
        """Subscribe to trade events for a product."""
        await self._native_client.subscribe_trades(product_symbol, speed)

    async def subscribe_orderbook(self, product_symbol: str, speed: str = "100ms") -> None:
        """Subscribe to incremental order book events for a product."""
        await self._native_client.subscribe_orderbook(product_symbol, speed)

    async def subscribe_partial_orderbook(self, product_symbol: str, levels: int = 5) -> None:
        """Subscribe to partial order book events for a product."""
        await self._native_client.subscribe_partial_orderbook(product_symbol, levels)

    async def subscribe_book_ticker(self, product_symbol: str, speed: str = "100ms") -> None:
        """Subscribe to book ticker events for a product."""
        await self._native_client.subscribe_book_ticker(product_symbol, speed)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        """Subscribe to kline events for a product."""
        await self._native_client.subscribe_klines(product_symbol, interval)

    async def recv(self) -> dict[str, Any] | list[Any] | bytes:
        """Receive one WebSocket event."""
        return _decode_event(await self._native_client.recv())


class PrivateClient(AsyncWebSocketMixin):
    """Async MEXC private WebSocket client."""

    def set_product_table(self, table: Any) -> None:  # noqa: ANN401
        """Use exact canonical/native symbols from a native ProductTable."""
        self._native_client.set_product_table(table)

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        """Create a MEXC private WebSocket client."""
        self._native_client = _native.MexcPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            ws_base_url=ws_base_url,
        )

    async def connect(self) -> str:
        """Open the WebSocket connection and return the listen key."""
        return str(await self._native_client.connect())

    async def keep_alive(self) -> str:
        """Extend the current listen key."""
        return str(await self._native_client.keep_alive())

    async def close_listen_key(self) -> None:
        """Invalidate the current listen key."""
        await self._native_client.close_listen_key()

    async def close(self) -> None:
        """Close the WebSocket connection and invalidate the listen key."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send an application-level ping."""
        await self._native_client.ping()

    async def subscribe(self, channels: list[str]) -> None:
        """Subscribe to raw MEXC private channels."""
        await self._native_client.subscribe(channels)

    async def unsubscribe(self, channels: list[str]) -> None:
        """Unsubscribe from raw MEXC private channels."""
        await self._native_client.unsubscribe(channels)

    async def subscribe_account(self) -> None:
        """Subscribe to account update events."""
        await self._native_client.subscribe_account()

    async def subscribe_deals(self) -> None:
        """Subscribe to account deal events."""
        await self._native_client.subscribe_deals()

    async def subscribe_orders(self) -> None:
        """Subscribe to account order events."""
        await self._native_client.subscribe_orders()

    def listen_key(self) -> str | None:
        """Return the active listen key, if one has been created."""
        listen_key = self._native_client.listen_key()
        return str(listen_key) if listen_key is not None else None

    async def recv(self) -> dict[str, Any] | list[Any] | bytes:
        """Receive one WebSocket event."""
        return _decode_event(await self._native_client.recv())


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async MEXC public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    timeout: float = 10.0,
    spot_http_base_url: str | None = None,
    ws_base_url: str | None = None,
) -> PrivateClient:
    """Create an async MEXC private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        timeout=timeout,
        spot_http_base_url=spot_http_base_url,
        ws_base_url=ws_base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]


class FuturesPublicClient(AsyncWebSocketMixin):
    """Contract JSON streams. Call ping every 10..20 seconds while connected."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a contract market data connection."""
        self._native_client = _native.MexcFuturesWebSocketClient(timeout=timeout, base_url=base_url)

    async def connect(self) -> None:
        """Connect to the contract endpoint."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send the contract protocol heartbeat."""
        await self._native_client.ping()

    async def recv(self) -> dict[str, Any] | list[Any] | bytes:
        """Receive the next contract event, including subscription acknowledgements."""
        return _decode_event(await self._native_client.recv())

    async def subscribe(
        self,
        channel: str,
        product_symbol: str | None = None,
        *,
        interval: str | None = None,
        step: str | None = None,
    ) -> None:
        """Subscribe using a channel suffix such as depth, funding.rate or kline."""
        await self._native_client.subscribe(channel, product_symbol, interval, step)

    async def unsubscribe(
        self,
        channel: str,
        product_symbol: str | None = None,
        *,
        interval: str | None = None,
        step: str | None = None,
    ) -> None:
        """Unsubscribe from a contract market channel."""
        await self._native_client.unsubscribe(channel, product_symbol, interval, step)

    async def subscribe_tickers(self) -> None:
        """Subscribe to all contract tickers."""
        await self.subscribe("tickers")

    async def subscribe_orderbook_step(self, product_symbol: str, step: str) -> None:
        """Subscribe to depth aggregated by the documented notional step."""
        await self.subscribe("depth.step", product_symbol, step=step)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        """Subscribe to contract candles using a native or canonical interval."""
        await self.subscribe("kline", product_symbol, interval=interval)

    async def subscribe_ticker(self, product_symbol: str) -> None:
        """Subscribe to the contract ticker channel."""
        await self.subscribe("ticker", product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        """Subscribe to the contract deal channel."""
        await self.subscribe("deal", product_symbol)

    async def subscribe_orderbook(self, product_symbol: str) -> None:
        """Subscribe to the contract depth channel."""
        await self.subscribe("depth", product_symbol)

    async def subscribe_funding_rate(self, product_symbol: str) -> None:
        """Subscribe to the contract funding.rate channel."""
        await self.subscribe("funding.rate", product_symbol)

    async def subscribe_index_price(self, product_symbol: str) -> None:
        """Subscribe to the contract index.price channel."""
        await self.subscribe("index.price", product_symbol)

    async def subscribe_fair_price(self, product_symbol: str) -> None:
        """Subscribe to the contract fair.price channel."""
        await self.subscribe("fair.price", product_symbol)


class FuturesPrivateClient(FuturesPublicClient):
    """Authenticated contract streams; all account events are pushed after login."""

    def set_product_table(self, table: Any) -> None:  # noqa: ANN401
        """Use exact canonical/native symbols from a native ProductTable."""
        self._native_client.set_product_table(table)

    def __init__(
        self, api_key: str, api_secret: str, timeout: float = 10.0, base_url: str | None = None
    ) -> None:
        """Create a contract connection that authenticates during connect."""
        self._native_client = _native.MexcFuturesWebSocketClient(
            timeout=timeout, base_url=base_url, api_key=api_key, api_secret=api_secret
        )

    async def set_private_filters(self, filters: list[dict[str, Any]]) -> None:
        """
        Replace account push filters; [] restores all default account events.

        Each entry has filter (e.g. order, order.deal, position, asset) and
        optional rules containing contract symbols. Filters replace prior rules.
        """
        await self._native_client.set_private_filters(json.dumps(filters))
