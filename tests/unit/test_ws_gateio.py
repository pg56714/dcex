# ruff: noqa: D100, D103

import pytest


class _FakeNativeGateioPublicWebSocketClient:
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.ping_count = 0
        self.subscriptions: list[tuple[str, list[str]]] = []
        self.unsubscriptions: list[tuple[str, list[str]]] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe(self, channel: str, payload: list[str]) -> None:
        self.subscriptions.append((channel, payload))

    async def unsubscribe(self, channel: str, payload: list[str]) -> None:
        self.unsubscriptions.append((channel, payload))

    async def subscribe_ticker(self, product_symbol: str) -> None:
        await self.subscribe("spot.tickers", [product_symbol])

    async def subscribe_trades(self, product_symbol: str) -> None:
        await self.subscribe("spot.trades", [product_symbol])

    async def subscribe_candlesticks(self, product_symbol: str, interval: str) -> None:
        await self.subscribe("spot.candlesticks", [interval, product_symbol])

    async def subscribe_book_ticker(self, product_symbol: str) -> None:
        await self.subscribe("spot.book_ticker", [product_symbol])

    async def subscribe_orderbook(self, product_symbol: str, speed: str = "100ms") -> None:
        await self.subscribe("spot.order_book_update", [product_symbol, speed])

    async def recv(self) -> bytes:
        return b'{"channel":"spot.trades","event":"update","result":[]}'


class _FakeNativeGateioPrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.ping_count = 0
        self.subscriptions: list[tuple[str, list[str]]] = []
        self.unsubscriptions: list[tuple[str, list[str]]] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe(self, channel: str, payload: list[str]) -> None:
        self.subscriptions.append((channel, payload))

    async def unsubscribe(self, channel: str, payload: list[str]) -> None:
        self.unsubscriptions.append((channel, payload))

    async def subscribe_orders(self, product_symbols: list[str]) -> None:
        await self.subscribe("spot.orders", product_symbols)

    async def subscribe_user_trades(self, product_symbols: list[str]) -> None:
        await self.subscribe("spot.usertrades", product_symbols)

    async def subscribe_balances(self) -> None:
        await self.subscribe("spot.balances", [])

    async def recv(self) -> bytes:
        return b'{"channel":"spot.balances","event":"update","result":[]}'


class _FakeNative:
    GateioPublicWebSocketClient = _FakeNativeGateioPublicWebSocketClient
    GateioPrivateWebSocketClient = _FakeNativeGateioPrivateWebSocketClient


@pytest.mark.asyncio
async def test_gateio_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import gateio

    monkeypatch.setattr(gateio, "_native", _FakeNative)

    async with gateio.public(timeout=2, base_url="wss://example.test/ws") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        await ws.subscribe_trades("BTC-USDT-SPOT")
        await ws.subscribe_ticker("BTC-USDT-SPOT")
        await ws.subscribe_candlesticks("BTC-USDT-SPOT", "1m")
        await ws.subscribe_book_ticker("BTC-USDT-SPOT")
        await ws.subscribe_orderbook("BTC-USDT-SPOT")
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        ("spot.trades", ["BTC-USDT-SPOT"]),
        ("spot.tickers", ["BTC-USDT-SPOT"]),
        ("spot.candlesticks", ["1m", "BTC-USDT-SPOT"]),
        ("spot.book_ticker", ["BTC-USDT-SPOT"]),
        ("spot.order_book_update", ["BTC-USDT-SPOT", "100ms"]),
    ]
    assert native_client.ping_count == 1
    assert event == {"channel": "spot.trades", "event": "update", "result": []}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_gateio_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import gateio

    class FakeNativeClient(_FakeNativeGateioPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        GateioPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(gateio, "_native", FakeNative)

    ws = gateio.public()
    with pytest.raises(RuntimeError, match="Unexpected Gate.io WebSocket event payload"):
        await ws.recv()


@pytest.mark.asyncio
async def test_gateio_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import gateio

    monkeypatch.setattr(gateio, "_native", _FakeNative)

    async with gateio.private(
        api_key="api-key",
        api_secret="api-secret",
        timeout=2,
        base_url="wss://example.test/ws",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        await ws.subscribe_orders(["BTC-USDT-SPOT"])
        await ws.subscribe_user_trades(["BTC-USDT-SPOT"])
        await ws.subscribe_balances()
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        ("spot.orders", ["BTC-USDT-SPOT"]),
        ("spot.usertrades", ["BTC-USDT-SPOT"]),
        ("spot.balances", []),
    ]
    assert native_client.ping_count == 1
    assert event == {"channel": "spot.balances", "event": "update", "result": []}
    assert native_client.closed is True
