"""Binance async WebSocket clients."""

import json
from typing import Any

from .._native_http import load_native
from ._base import AsyncWebSocketMixin

_native = load_native()


class PublicClient(AsyncWebSocketMixin):
    """Async Binance Spot public market WebSocket client."""

    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        """Create a Binance public WebSocket client."""
        self._native_client = _native.BinancePublicWebSocketClient(
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
        """Subscribe to raw Binance stream names."""
        return int(await self._native_client.subscribe(streams))

    async def unsubscribe(self, streams: list[str]) -> int:
        """Unsubscribe from raw Binance stream names."""
        return int(await self._native_client.unsubscribe(streams))

    async def subscribe_trades(self, product_symbol: str) -> int:
        """Subscribe to raw trade events for a product."""
        return int(await self._native_client.subscribe_trades(product_symbol))

    async def subscribe_agg_trades(self, product_symbol: str) -> int:
        """Subscribe to aggregate trade events for a product."""
        return int(await self._native_client.subscribe_agg_trades(product_symbol))

    async def subscribe_orderbook(self, product_symbol: str) -> int:
        """Subscribe to diff order book events for a product."""
        return int(await self._native_client.subscribe_orderbook(product_symbol))

    async def subscribe_ticker(self, product_symbol: str) -> int:
        """Subscribe to ticker events for a product."""
        return int(await self._native_client.subscribe_ticker(product_symbol))

    async def subscribe_klines(self, product_symbol: str, interval: str) -> int:
        """Subscribe to kline events for a product."""
        return int(await self._native_client.subscribe_klines(product_symbol, interval))

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Binance WebSocket event payload: {event!r}")


class PrivateClient(AsyncWebSocketMixin):
    """Async Binance futures private user data WebSocket client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        """Create a Binance private WebSocket client."""
        self._native_client = _native.BinancePrivateWebSocketClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            spot_http_base_url=spot_http_base_url,
            futures_http_base_url=futures_http_base_url,
            ws_base_url=ws_base_url,
        )

    async def connect(self) -> str:
        """Open the WebSocket connection and return the listen key."""
        return str(await self._native_client.connect())

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
        raise RuntimeError(f"Unexpected Binance WebSocket event payload: {event!r}")


class EquityClient(AsyncWebSocketMixin):
    """Async Binance Equity WebSocket client for one documented stock stream."""

    def __init__(
        self,
        stream: str,
        product_symbol: str | None = None,
        interval: str | None = None,
        listen_key: str | None = None,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create a Binance Equity market-data or order-report stream."""
        self._native_client = _native.BinanceEquityWebSocketClient(
            stream=stream,
            product_symbol=product_symbol,
            interval=interval,
            listen_key=listen_key,
            timeout=timeout,
            base_url=base_url,
        )

    @property
    def url(self) -> str:
        """Return the resolved Binance Equity WebSocket URL."""
        return str(self._native_client.url())

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._native_client.close()

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive and decode one Equity WebSocket event."""
        body = await self._native_client.recv()
        event = json.loads(bytes(body))
        if isinstance(event, dict | list):
            return event
        raise RuntimeError(f"Unexpected Binance Equity WebSocket event payload: {event!r}")


def public(timeout: float = 10.0, base_url: str | None = None) -> PublicClient:
    """Create an async Binance Spot public market WebSocket client."""
    return PublicClient(timeout=timeout, base_url=base_url)


def private(
    api_key: str,
    api_secret: str,
    timeout: float = 10.0,
    spot_http_base_url: str | None = None,
    futures_http_base_url: str | None = None,
    ws_base_url: str | None = None,
) -> PrivateClient:
    """Create an async Binance futures private user data WebSocket client."""
    return PrivateClient(
        api_key=api_key,
        api_secret=api_secret,
        timeout=timeout,
        spot_http_base_url=spot_http_base_url,
        futures_http_base_url=futures_http_base_url,
        ws_base_url=ws_base_url,
    )


def equity(
    stream: str,
    product_symbol: str | None = None,
    interval: str | None = None,
    listen_key: str | None = None,
    timeout: float = 10.0,
    base_url: str | None = None,
) -> EquityClient:
    """Create a Binance Equity market-data or order-report WebSocket client."""
    return EquityClient(
        stream=stream,
        product_symbol=product_symbol,
        interval=interval,
        listen_key=listen_key,
        timeout=timeout,
        base_url=base_url,
    )


__all__ = ["EquityClient", "PrivateClient", "PublicClient", "equity", "private", "public"]


class ApiClient(AsyncWebSocketMixin):
    """
    JSON WebSocket API with concurrent reads/writes and server-ping handling.

    Native Binance symbol names and parameter names are used. Quantities and
    prices are decimal strings; timestamps and IDs are integers. Read responses
    with ``recv`` and match their ``id`` to the integer returned by each request.
    Errors, partial results and user events are returned intact. Reconcile orders
    after a connection failure; this client does not retry trading requests.
    """

    def __init__(
        self,
        market: str = "spot",
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        ed25519_seed: str | None = None,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Use HMAC secret or a 64-character hexadecimal Ed25519 seed with the API key."""
        self._native_client = _native.BinanceWebSocketApiClient(
            market=market,
            api_key=api_key,
            api_secret=api_secret,
            ed25519_seed=ed25519_seed,
            timeout=timeout,
            base_url=base_url,
        )

    async def connect(self) -> None:
        """Connect; authentication is applied to individual signed requests."""
        await self._native_client.connect()

    async def close(self) -> None:
        """Close the API connection."""
        await self._native_client.close()

    async def request(self, method: str, params: dict[str, Any] | None = None) -> int:
        """Send a documented method and return its correlation ID after writing."""
        return int(
            await self._native_client.request(method, json.dumps(params or {}, allow_nan=False))
        )

    async def recv(self) -> dict[str, Any]:
        """Read a complete response or user event without suppressing API errors."""
        event = json.loads(bytes(await self._native_client.recv()))
        if not isinstance(event, dict):
            raise TypeError("Unexpected Binance WebSocket API response type")
        return event


class SpotApiClient(ApiClient):
    """Binance spot WebSocket trading, account and market API."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        ed25519_seed: str | None = None,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create the spot API connection using HMAC or Ed25519 credentials."""
        super().__init__(
            "spot",
            api_key,
            api_secret,
            ed25519_seed=ed25519_seed,
            timeout=timeout,
            base_url=base_url,
        )

    async def ping(self, params: dict[str, Any] | None = None) -> int:
        """Send ``ping``; return the request ID and read the result with ``recv``."""
        return await self.request("ping", params)

    async def time(self, params: dict[str, Any] | None = None) -> int:
        """Send ``time``; return the request ID and read the result with ``recv``."""
        return await self.request("time", params)

    async def exchange_info(self, params: dict[str, Any] | None = None) -> int:
        """Send ``exchangeInfo``; return the request ID and read the result with ``recv``."""
        return await self.request("exchangeInfo", params)

    async def execution_rules(self, params: dict[str, Any] | None = None) -> int:
        """Send ``executionRules``; return the request ID and read the result with ``recv``."""
        return await self.request("executionRules", params)

    async def get_orderbook(self, params: dict[str, Any] | None = None) -> int:
        """Send ``depth``; return the request ID and read the result with ``recv``."""
        return await self.request("depth", params)

    async def trades_recent(self, params: dict[str, Any] | None = None) -> int:
        """Send ``trades.recent``; return the request ID and read the result with ``recv``."""
        return await self.request("trades.recent", params)

    async def trades_historical(self, params: dict[str, Any] | None = None) -> int:
        """Send ``trades.historical``; return the request ID and read the result with ``recv``."""
        return await self.request("trades.historical", params)

    async def block_trades_historical(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``blockTrades.historical``; return the request ID and read the result with
        ``recv``.
        """
        return await self.request("blockTrades.historical", params)

    async def trades_aggregate(self, params: dict[str, Any] | None = None) -> int:
        """Send ``trades.aggregate``; return the request ID and read the result with ``recv``."""
        return await self.request("trades.aggregate", params)

    async def klines(self, params: dict[str, Any] | None = None) -> int:
        """Send ``klines``; return the request ID and read the result with ``recv``."""
        return await self.request("klines", params)

    async def ui_klines(self, params: dict[str, Any] | None = None) -> int:
        """Send ``uiKlines``; return the request ID and read the result with ``recv``."""
        return await self.request("uiKlines", params)

    async def avg_price(self, params: dict[str, Any] | None = None) -> int:
        """Send ``avgPrice``; return the request ID and read the result with ``recv``."""
        return await self.request("avgPrice", params)

    async def ticker_24hr(self, params: dict[str, Any] | None = None) -> int:
        """Send ``ticker.24hr``; return the request ID and read the result with ``recv``."""
        return await self.request("ticker.24hr", params)

    async def ticker_trading_day(self, params: dict[str, Any] | None = None) -> int:
        """Send ``ticker.tradingDay``; return the request ID and read the result with ``recv``."""
        return await self.request("ticker.tradingDay", params)

    async def ticker(self, params: dict[str, Any] | None = None) -> int:
        """Send ``ticker``; return the request ID and read the result with ``recv``."""
        return await self.request("ticker", params)

    async def get_price(self, params: dict[str, Any] | None = None) -> int:
        """Send ``ticker.price``; return the request ID and read the result with ``recv``."""
        return await self.request("ticker.price", params)

    async def get_book_ticker(self, params: dict[str, Any] | None = None) -> int:
        """Send ``ticker.book``; return the request ID and read the result with ``recv``."""
        return await self.request("ticker.book", params)

    async def reference_price(self, params: dict[str, Any] | None = None) -> int:
        """Send ``referencePrice``; return the request ID and read the result with ``recv``."""
        return await self.request("referencePrice", params)

    async def reference_price_calculation(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``referencePrice.calculation``; return the request ID and read the result with
        ``recv``.
        """
        return await self.request("referencePrice.calculation", params)

    async def logon(self, params: dict[str, Any] | None = None) -> int:
        """Send ``session.logon``; return the request ID and read the result with ``recv``."""
        return await self.request("session.logon", params)

    async def get_session(self, params: dict[str, Any] | None = None) -> int:
        """Send ``session.status``; return the request ID and read the result with ``recv``."""
        return await self.request("session.status", params)

    async def logout(self, params: dict[str, Any] | None = None) -> int:
        """Send ``session.logout``; return the request ID and read the result with ``recv``."""
        return await self.request("session.logout", params)

    async def place_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.place``; return the request ID and read the result with ``recv``."""
        return await self.request("order.place", params)

    async def test_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.test``; return the request ID and read the result with ``recv``."""
        return await self.request("order.test", params)

    async def cancel_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.cancel``; return the request ID and read the result with ``recv``."""
        return await self.request("order.cancel", params)

    async def cancel_replace_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.cancelReplace``; return the request ID and read the result with ``recv``."""
        return await self.request("order.cancelReplace", params)

    async def amend_order_keep_priority(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``order.amend.keepPriority``; return the request ID and read the result with
        ``recv``.
        """
        return await self.request("order.amend.keepPriority", params)

    async def cancel_all_orders(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``openOrders.cancelAll``; return the request ID and read the result with ``recv``.
        """
        return await self.request("openOrders.cancelAll", params)

    async def order_list_place_oco(self, params: dict[str, Any] | None = None) -> int:
        """Send ``orderList.place.oco``; return the request ID and read the result with ``recv``."""
        return await self.request("orderList.place.oco", params)

    async def order_list_place_oto(self, params: dict[str, Any] | None = None) -> int:
        """Send ``orderList.place.oto``; return the request ID and read the result with ``recv``."""
        return await self.request("orderList.place.oto", params)

    async def order_list_place_otoco(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``orderList.place.otoco``; return the request ID and read the result with ``recv``.
        """
        return await self.request("orderList.place.otoco", params)

    async def order_list_place_opo(self, params: dict[str, Any] | None = None) -> int:
        """Send ``orderList.place.opo``; return the request ID and read the result with ``recv``."""
        return await self.request("orderList.place.opo", params)

    async def order_list_place_opoco(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``orderList.place.opoco``; return the request ID and read the result with ``recv``.
        """
        return await self.request("orderList.place.opoco", params)

    async def order_list_cancel(self, params: dict[str, Any] | None = None) -> int:
        """Send ``orderList.cancel``; return the request ID and read the result with ``recv``."""
        return await self.request("orderList.cancel", params)

    async def sor_order_place(self, params: dict[str, Any] | None = None) -> int:
        """Send ``sor.order.place``; return the request ID and read the result with ``recv``."""
        return await self.request("sor.order.place", params)

    async def sor_order_test(self, params: dict[str, Any] | None = None) -> int:
        """Send ``sor.order.test``; return the request ID and read the result with ``recv``."""
        return await self.request("sor.order.test", params)

    async def get_account(self, params: dict[str, Any] | None = None) -> int:
        """Send ``account.status``; return the request ID and read the result with ``recv``."""
        return await self.request("account.status", params)

    async def get_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.status``; return the request ID and read the result with ``recv``."""
        return await self.request("order.status", params)

    async def open_orders_status(self, params: dict[str, Any] | None = None) -> int:
        """Send ``openOrders.status``; return the request ID and read the result with ``recv``."""
        return await self.request("openOrders.status", params)

    async def all_orders(self, params: dict[str, Any] | None = None) -> int:
        """Send ``allOrders``; return the request ID and read the result with ``recv``."""
        return await self.request("allOrders", params)

    async def order_list_status(self, params: dict[str, Any] | None = None) -> int:
        """Send ``orderList.status``; return the request ID and read the result with ``recv``."""
        return await self.request("orderList.status", params)

    async def open_order_lists_status(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``openOrderLists.status``; return the request ID and read the result with ``recv``.
        """
        return await self.request("openOrderLists.status", params)

    async def all_order_lists(self, params: dict[str, Any] | None = None) -> int:
        """Send ``allOrderLists``; return the request ID and read the result with ``recv``."""
        return await self.request("allOrderLists", params)

    async def my_trades(self, params: dict[str, Any] | None = None) -> int:
        """Send ``myTrades``; return the request ID and read the result with ``recv``."""
        return await self.request("myTrades", params)

    async def account_rate_limits_orders(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``account.rateLimits.orders``; return the request ID and read the result with
        ``recv``.
        """
        return await self.request("account.rateLimits.orders", params)

    async def my_prevented_matches(self, params: dict[str, Any] | None = None) -> int:
        """Send ``myPreventedMatches``; return the request ID and read the result with ``recv``."""
        return await self.request("myPreventedMatches", params)

    async def my_allocations(self, params: dict[str, Any] | None = None) -> int:
        """Send ``myAllocations``; return the request ID and read the result with ``recv``."""
        return await self.request("myAllocations", params)

    async def account_commission(self, params: dict[str, Any] | None = None) -> int:
        """Send ``account.commission``; return the request ID and read the result with ``recv``."""
        return await self.request("account.commission", params)

    async def order_amendments(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.amendments``; return the request ID and read the result with ``recv``."""
        return await self.request("order.amendments", params)

    async def my_filters(self, params: dict[str, Any] | None = None) -> int:
        """Send ``myFilters``; return the request ID and read the result with ``recv``."""
        return await self.request("myFilters", params)

    async def subscribe_session_user_data(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``userDataStream.subscribe``; return the request ID and read the result with
        ``recv``.
        """
        return await self.request("userDataStream.subscribe", params)

    async def unsubscribe_user_data(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``userDataStream.unsubscribe``; return the request ID and read the result with
        ``recv``.
        """
        return await self.request("userDataStream.unsubscribe", params)

    async def get_subscriptions(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``session.subscriptions``; return the request ID and read the result with ``recv``.
        """
        return await self.request("session.subscriptions", params)

    async def subscribe_user_data(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``userDataStream.subscribe.signature``; return the request ID and read the result
        with ``recv``.
        """
        return await self.request("userDataStream.subscribe.signature", params)


class FuturesApiClient(ApiClient):
    """Binance futures WebSocket trading, account and market API."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        ed25519_seed: str | None = None,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create the futures API connection using HMAC or Ed25519 credentials."""
        super().__init__(
            "futures",
            api_key,
            api_secret,
            ed25519_seed=ed25519_seed,
            timeout=timeout,
            base_url=base_url,
        )

    async def place_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.place``; return the request ID and read the result with ``recv``."""
        return await self.request("order.place", params)

    async def amend_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.modify``; return the request ID and read the result with ``recv``."""
        return await self.request("order.modify", params)

    async def cancel_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.cancel``; return the request ID and read the result with ``recv``."""
        return await self.request("order.cancel", params)

    async def get_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.status``; return the request ID and read the result with ``recv``."""
        return await self.request("order.status", params)

    async def place_algo_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``algoOrder.place``; return the request ID and read the result with ``recv``."""
        return await self.request("algoOrder.place", params)

    async def cancel_algo_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``algoOrder.cancel``; return the request ID and read the result with ``recv``."""
        return await self.request("algoOrder.cancel", params)

    async def get_account(self, params: dict[str, Any] | None = None) -> int:
        """Send ``v2/account.status``; return the request ID and read the result with ``recv``."""
        return await self.request("v2/account.status", params)

    async def get_balance(self, params: dict[str, Any] | None = None) -> int:
        """Send ``v2/account.balance``; return the request ID and read the result with ``recv``."""
        return await self.request("v2/account.balance", params)

    async def get_positions(self, params: dict[str, Any] | None = None) -> int:
        """Send ``v2/account.position``; return the request ID and read the result with ``recv``."""
        return await self.request("v2/account.position", params)

    async def get_orderbook(self, params: dict[str, Any] | None = None) -> int:
        """Send ``depth``; return the request ID and read the result with ``recv``."""
        return await self.request("depth", params)

    async def get_price(self, params: dict[str, Any] | None = None) -> int:
        """Send ``ticker.price``; return the request ID and read the result with ``recv``."""
        return await self.request("ticker.price", params)

    async def get_book_ticker(self, params: dict[str, Any] | None = None) -> int:
        """Send ``ticker.book``; return the request ID and read the result with ``recv``."""
        return await self.request("ticker.book", params)

    async def create_listen_key(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``userDataStream.start``; return the request ID and read the result with ``recv``.
        """
        return await self.request("userDataStream.start", params)

    async def keep_alive_listen_key(self, params: dict[str, Any] | None = None) -> int:
        """Send ``userDataStream.ping``; return the request ID and read the result with ``recv``."""
        return await self.request("userDataStream.ping", params)

    async def close_listen_key(self, params: dict[str, Any] | None = None) -> int:
        """Send ``userDataStream.stop``; return the request ID and read the result with ``recv``."""
        return await self.request("userDataStream.stop", params)

    async def logon(self, params: dict[str, Any] | None = None) -> int:
        """Send ``session.logon``; return the request ID and read the result with ``recv``."""
        return await self.request("session.logon", params)

    async def get_session(self, params: dict[str, Any] | None = None) -> int:
        """Send ``session.status``; return the request ID and read the result with ``recv``."""
        return await self.request("session.status", params)

    async def logout(self, params: dict[str, Any] | None = None) -> int:
        """Send ``session.logout``; return the request ID and read the result with ``recv``."""
        return await self.request("session.logout", params)


class CoinFuturesApiClient(ApiClient):
    """Binance COIN-M WebSocket trading and account API."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        ed25519_seed: str | None = None,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        """Create the futures API connection using HMAC or Ed25519 credentials."""
        super().__init__(
            "coin_futures",
            api_key,
            api_secret,
            ed25519_seed=ed25519_seed,
            timeout=timeout,
            base_url=base_url,
        )

    async def place_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.place``; return the request ID and read the result with ``recv``."""
        return await self.request("order.place", params)

    async def amend_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.modify``; return the request ID and read the result with ``recv``."""
        return await self.request("order.modify", params)

    async def cancel_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.cancel``; return the request ID and read the result with ``recv``."""
        return await self.request("order.cancel", params)

    async def get_order(self, params: dict[str, Any] | None = None) -> int:
        """Send ``order.status``; return the request ID and read the result with ``recv``."""
        return await self.request("order.status", params)

    async def get_account(self, params: dict[str, Any] | None = None) -> int:
        """Send ``account.status``; return the request ID and read the result with ``recv``."""
        return await self.request("account.status", params)

    async def get_balance(self, params: dict[str, Any] | None = None) -> int:
        """Send ``account.balance``; return the request ID and read the result with ``recv``."""
        return await self.request("account.balance", params)

    async def get_positions(self, params: dict[str, Any] | None = None) -> int:
        """Send ``account.position``; return the request ID and read the result with ``recv``."""
        return await self.request("account.position", params)

    async def create_listen_key(self, params: dict[str, Any] | None = None) -> int:
        """
        Send ``userDataStream.start``; return the request ID and read the result with ``recv``.
        """
        return await self.request("userDataStream.start", params)

    async def keep_alive_listen_key(self, params: dict[str, Any] | None = None) -> int:
        """Send ``userDataStream.ping``; return the request ID and read the result with ``recv``."""
        return await self.request("userDataStream.ping", params)

    async def close_listen_key(self, params: dict[str, Any] | None = None) -> int:
        """Send ``userDataStream.stop``; return the request ID and read the result with ``recv``."""
        return await self.request("userDataStream.stop", params)
