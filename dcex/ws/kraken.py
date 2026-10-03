"""Kraken async WebSocket clients."""

import json
from typing import Any

from dcex._input_validation import normalize_endpoint
from dcex._schema_codec import encode_json

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Kraken Spot public market WebSocket client."""

    def set_product_table(self, table: Any) -> None:  # noqa: ANN401
        """Use exact canonical/native symbols from a native ProductTable."""
        self._native_client.set_product_table(table)

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a Kraken public WebSocket client."""
        self._native_client = _native.KrakenPublicWebSocketClient(
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> int:
        """Send an application-level ping."""
        return int(await self._native_client.ping())

    async def subscribe_channel(self, channel: str, product_symbols: list[str]) -> int:
        """Subscribe to a Kraken public channel."""
        return int(await self._native_client.subscribe_channel(channel, product_symbols))

    async def unsubscribe_channel(self, channel: str, product_symbols: list[str]) -> int:
        """Unsubscribe from a Kraken public channel."""
        return int(await self._native_client.unsubscribe_channel(channel, product_symbols))

    async def subscribe_ticker(
        self,
        product_symbol: str,
        event_trigger: str = "trades",
        snapshot: bool = True,
    ) -> int:
        """Subscribe to ticker events for a product."""
        return int(
            await self._native_client.subscribe_ticker(product_symbol, event_trigger, snapshot)
        )

    async def subscribe_trades(self, product_symbol: str, snapshot: bool = False) -> int:
        """Subscribe to trade events for a product."""
        return int(await self._native_client.subscribe_trades(product_symbol, snapshot))

    async def subscribe_orderbook(
        self, product_symbol: str, depth: int = 10, snapshot: bool = True
    ) -> int:
        """Subscribe to order book events for a product."""
        return int(await self._native_client.subscribe_orderbook(product_symbol, depth, snapshot))

    async def subscribe_klines(
        self, product_symbol: str, interval: int = 1, snapshot: bool = True
    ) -> int:
        """Subscribe to OHLC candle events for a product."""
        return int(await self._native_client.subscribe_klines(product_symbol, interval, snapshot))

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Kraken WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Kraken private WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        """Create a Kraken private WebSocket client."""
        self._native_client = _native.KrakenPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            ws_base_url=ws_base_url,
        )

    async def connect(self) -> str:
        """Fetch a token and open the WebSocket connection."""
        return str(await self._native_client.connect())

    async def fetch_token(self) -> str:
        """Fetch and store a Kraken WebSocket token."""
        return str(await self._native_client.fetch_token())

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def ping(self) -> int:
        """Send an application-level ping."""
        return int(await self._native_client.ping())

    async def subscribe_balances(
        self,
        snapshot: bool = True,
        rebased: bool = True,
        users: str | None = None,
    ) -> int:
        """Subscribe to balance update events."""
        return int(await self._native_client.subscribe_balances(snapshot, rebased, users))

    async def unsubscribe_balances(self) -> int:
        """Unsubscribe from balance update events."""
        return int(await self._native_client.unsubscribe_balances())

    async def subscribe_executions(
        self,
        snap_orders: bool = True,
        snap_trades: bool = False,
        order_status: bool = True,
        rebased: bool = True,
        ratecounter: bool = False,
        users: str | None = None,
    ) -> int:
        """Subscribe to order status and execution events."""
        return int(
            await self._native_client.subscribe_executions(
                snap_orders,
                snap_trades,
                order_status,
                rebased,
                ratecounter,
                users,
            )
        )

    async def unsubscribe_executions(self) -> int:
        """Unsubscribe from order status and execution events."""
        return int(await self._native_client.unsubscribe_executions())

    def token(self) -> str | None:
        """Return the current WebSocket token if one has been fetched."""
        token = self._native_client.token()
        return str(token) if token is not None else None

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Kraken WebSocket event payload: {event!r}")

    async def trade_request(self, method: str, params: dict[str, Any]) -> int:
        """Send a Spot v2 trade request using native JSON fields; correlate recv() by req_id."""
        return int(await self._native_client.trade_request(method, json.dumps(params)))

    async def add_order(self, params: dict[str, Any]) -> int:
        """Send add_order; numeric order fields must be JSON numbers and symbols use BTC/USD."""
        return await self.trade_request("add_order", params)

    async def amend_order(self, params: dict[str, Any]) -> int:
        """Send amend_order; numeric order fields must be JSON numbers and symbols use BTC/USD."""
        return await self.trade_request("amend_order", params)

    async def cancel_order(self, params: dict[str, Any]) -> int:
        """Send cancel_order; numeric order fields must be JSON numbers and symbols use BTC/USD."""
        return await self.trade_request("cancel_order", params)

    async def batch_add(self, params: dict[str, Any]) -> int:
        """Send batch_add; numeric order fields must be JSON numbers and symbols use BTC/USD."""
        return await self.trade_request("batch_add", params)

    async def batch_cancel(self, params: dict[str, Any]) -> int:
        """Send batch_cancel; numeric order fields must be JSON numbers and symbols use BTC/USD."""
        return await self.trade_request("batch_cancel", params)

    async def cancel_all(self) -> int:
        """Cancel all open Spot orders."""
        return await self.trade_request("cancel_all", {})

    async def cancel_after(self, timeout: int) -> int:  # noqa: ASYNC109 - exchange cancel timer
        """Set the cancel timer in seconds; zero disables it, refresh before expiry."""
        return await self.trade_request("cancel_after", {"timeout": timeout})


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async Kraken Spot public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    timeout: float = 10.0,
    spot_http_base_url: str | None = None,
    ws_base_url: str | None = None,
) -> PrivateClient:
    """Create an async Kraken private WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        timeout=timeout,
        spot_http_base_url=spot_http_base_url,
        ws_base_url=ws_base_url,
    )


__all__ = ["PrivateClient", "PublicClient", "private", "public"]


class FuturesPublicClient(AsyncWebSocketMixin):
    """Kraken Derivatives streaming; ping every 60 seconds and resubscribe after reconnect."""

    def set_product_table(self, table: Any) -> None:  # noqa: ANN401
        """Use exact canonical/native symbols from a native ProductTable."""
        self._native_client.set_product_table(table)

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a public derivatives stream client."""
        self._native_client = _native.KrakenFuturesWebSocketClient(
            timeout=timeout, base_url=base_url
        )

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the connection."""
        await self._native_client.close()

    async def ping(self) -> None:
        """Send a WebSocket ping frame."""
        await self._native_client.ping()

    async def subscribe(self, feed: str, product_ids: list[str] | None = None) -> None:
        """
        Subscribe; canonical SWAP symbols map to PF_ contracts, other contracts use native IDs.
        """
        await self._native_client.subscribe(feed, product_ids)

    async def unsubscribe(self, feed: str, product_ids: list[str] | None = None) -> None:
        """Remove a feed subscription."""
        await self._native_client.unsubscribe(feed, product_ids)

    async def recv(self) -> dict[str, Any]:
        """Receive one event, including subscription errors and sequence fields unchanged."""
        event = json.loads(bytes(await self._native_client.recv()))
        if not isinstance(event, dict):
            raise TypeError("Unexpected Kraken futures event")
        return event

    async def subscribe_orderbook(self, product_ids: list[str]) -> None:
        """Subscribe to the book feed."""
        await self.subscribe("book", product_ids)

    async def subscribe_ticker(self, product_ids: list[str]) -> None:
        """Subscribe to the ticker feed."""
        await self.subscribe("ticker", product_ids)

    async def subscribe_ticker_lite(self, product_ids: list[str]) -> None:
        """Subscribe to the ticker_lite feed."""
        await self.subscribe("ticker_lite", product_ids)

    async def subscribe_trades(self, product_ids: list[str]) -> None:
        """Subscribe to the trade feed."""
        await self.subscribe("trade", product_ids)

    async def subscribe_heartbeat(self) -> None:
        """Subscribe to exchange heartbeat events."""
        await self.subscribe("heartbeat")


class FuturesPrivateClient(FuturesPublicClient):
    """Kraken Derivatives account streams with signed-challenge authentication."""

    def __init__(
        self, api_key: str, api_secret: str, timeout: float = 10.0, base_url: str | None = None
    ) -> None:
        """Create a private derivatives client with a Base64 API secret."""
        self._native_client = _native.KrakenFuturesWebSocketClient(
            timeout=timeout, base_url=base_url, api_key=api_key, api_secret=api_secret
        )

    async def subscribe_fills(self, product_ids: list[str] | None = None) -> None:
        """Subscribe to executions, optionally filtered by contract."""
        await self.subscribe("fills", product_ids)

    async def subscribe_open_orders(self) -> None:
        """Subscribe to the open_orders account feed."""
        await self.subscribe("open_orders")

    async def subscribe_open_orders_verbose(self) -> None:
        """Subscribe to the open_orders_verbose account feed."""
        await self.subscribe("open_orders_verbose")

    async def subscribe_positions(self) -> None:
        """Subscribe to the open_position account feed."""
        await self.subscribe("open_position")

    async def subscribe_balances(self) -> None:
        """Subscribe to the balances account feed."""
        await self.subscribe("balances")

    async def subscribe_account_log(self) -> None:
        """Subscribe to the account_log account feed."""
        await self.subscribe("account_log")

    async def subscribe_notifications(self) -> None:
        """Subscribe to the notifications account feed."""
        await self.subscribe("notifications")


class Level3Client(AsyncWebSocketMixin):
    """
    Kraken authenticated L3 feed at ws-l3.kraken.com/v2.

    Returns raw snapshots, updates, checksums and per-symbol acknowledgements.
    Maintain book state and verify checksums in the consuming trading system.
    Subscription rate and the 200-symbol connection limit are enforced by Kraken.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        """Create a dedicated L3 connection using a REST WebSocket token."""
        self._native_client = _native.KrakenPrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            ws_base_url=ws_base_url or "wss://ws-l3.kraken.com/v2",
        )

    async def connect(self) -> str:
        """Fetch a token and connect to the L3 service."""
        return str(await self._native_client.connect())

    async def close(self) -> None:
        """Close the connection."""
        await self._native_client.close()

    async def ping(self) -> int:
        """Send an application ping."""
        return int(await self._native_client.ping())

    async def subscribe_level3(
        self, product_symbols: list[str], depth: int = 10, snapshot: bool = True
    ) -> int:
        """Subscribe to depth 10, 100 or 1000; read acknowledgements with recv."""
        return int(await self._native_client.subscribe_level3(product_symbols, depth, snapshot))

    async def unsubscribe_level3(self, product_symbols: list[str], depth: int = 10) -> int:
        """Cancel subscriptions at their original depth."""
        return int(await self._native_client.unsubscribe_level3(product_symbols, depth))

    async def recv(self) -> dict[str, Any]:
        """Return one complete event, retaining order IDs and checksum."""
        event = json.loads(bytes(await self._native_client.recv()))
        if not isinstance(event, dict):
            raise TypeError("Unexpected Kraken L3 event")
        return event


class V1Client(AsyncWebSocketMixin):
    """
    Kraken Spot V1 event/subscription protocol, including array event payloads.

    Use a REST GetWebSocketsToken token for private channels and trading.
    Check acknowledgement status events received with `recv` after sending.
    """

    def __init__(
        self, token: str | None = None, *, timeout: float = 10.0, base_url: str | None = None
    ) -> None:
        """Select the V1 public endpoint or the private endpoint when token is set."""
        self._native_client = _native.KrakenV1WebSocketClient(token, timeout, base_url)

    async def connect(self) -> None:
        """Open V1; the initial systemStatus event remains available via recv."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close this connection."""
        await self._native_client.close()

    async def send_message(self, message: dict[str, Any], *, all_symbols: bool = False) -> None:
        """Send a documented V1 event; cancelAll/countdown require all_symbols=True."""
        message = normalize_endpoint(
            "kraken", str(message.get("event", "")), message, websocket=True
        )
        await self._native_client.send_message(encode_json(message), all_symbols)

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive a raw V1 status or market/account event."""
        return json.loads(bytes(await self._native_client.recv()))
