# ruff: noqa: D100, D103

import pytest


class _FakeNativeBitmartPublicWebSocketClient:
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.ping_count = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []
        self.snapshot_requests: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe(self, topics: list[str]) -> None:
        self.subscriptions.extend(topics)

    async def unsubscribe(self, topics: list[str]) -> None:
        self.unsubscriptions.extend(topics)

    async def request_depth_snapshot(self, product_symbol: str) -> None:
        self.snapshot_requests.append(product_symbol)

    async def subscribe_ticker(self, product_symbol: str) -> None:
        await self.subscribe([f"spot/ticker:{product_symbol}"])

    async def subscribe_book_ticker(self, product_symbol: str) -> None:
        await self.subscribe([f"spot/bookTicker:{product_symbol}"])

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        await self.subscribe([f"spot/kline{interval}:{product_symbol}"])

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 20) -> None:
        await self.subscribe([f"spot/depth{depth}:{product_symbol}"])

    async def subscribe_depth_increase(self, product_symbol: str) -> None:
        await self.subscribe([f"spot/depth/increase100:{product_symbol}"])

    async def subscribe_trades(self, product_symbol: str) -> None:
        await self.subscribe([f"spot/trade:{product_symbol}"])

    async def recv(self) -> bytes:
        return b'{"event":"subscribe","topic":"spot/trade:BTC_USDT"}'


class _FakeNativeBitmartPrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        memo: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = memo
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.logged_in = False
        self.ping_count = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True
        self.logged_in = True

    async def login(self) -> None:
        self.logged_in = True

    async def close(self) -> None:
        self.closed = True
        self.logged_in = False

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe(self, topics: list[str]) -> None:
        self.subscriptions.extend(topics)

    async def unsubscribe(self, topics: list[str]) -> None:
        self.unsubscriptions.extend(topics)

    async def subscribe_orders(self, product_symbol: str | None = None) -> None:
        topic = (
            f"spot/user/order:{product_symbol}"
            if product_symbol is not None
            else "spot/user/orders:ALL_SYMBOLS"
        )
        await self.subscribe([topic])

    async def subscribe_balance(self) -> None:
        await self.subscribe(["spot/user/balance:BALANCE_UPDATE"])

    def is_logged_in(self) -> bool:
        return self.logged_in

    async def recv(self) -> bytes:
        return b'{"event":"subscribe","topic":"spot/user/balance:BALANCE_UPDATE"}'


class _FakeNative:
    BitmartPublicWebSocketClient = _FakeNativeBitmartPublicWebSocketClient
    BitmartPrivateWebSocketClient = _FakeNativeBitmartPrivateWebSocketClient


@pytest.mark.asyncio
async def test_bitmart_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitmart

    monkeypatch.setattr(bitmart, "_native", _FakeNative)

    async with bitmart.public(timeout=2, base_url="wss://example.test/ws") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        await ws.subscribe_trades("BTC-USDT-SPOT")
        await ws.subscribe_orderbook("BTC-USDT-SPOT", depth=20)
        await ws.subscribe_klines("BTC-USDT-SPOT", "1m")
        await ws.subscribe_book_ticker("BTC-USDT-SPOT")
        await ws.subscribe_depth_increase("BTC-USDT-SPOT")
        await ws.request_depth_snapshot("BTC-USDT-SPOT")
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        "spot/trade:BTC-USDT-SPOT",
        "spot/depth20:BTC-USDT-SPOT",
        "spot/kline1m:BTC-USDT-SPOT",
        "spot/bookTicker:BTC-USDT-SPOT",
        "spot/depth/increase100:BTC-USDT-SPOT",
    ]
    assert native_client.snapshot_requests == ["BTC-USDT-SPOT"]
    assert native_client.ping_count == 1
    assert event == {"event": "subscribe", "topic": "spot/trade:BTC_USDT"}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_bitmart_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitmart

    class FakeNativeClient(_FakeNativeBitmartPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b"1"

    class FakeNative:
        BitmartPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(bitmart, "_native", FakeNative)

    ws = bitmart.public()
    with pytest.raises(RuntimeError, match="Unexpected BitMart WebSocket event payload"):
        await ws.recv()


@pytest.mark.asyncio
async def test_bitmart_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitmart

    monkeypatch.setattr(bitmart, "_native", _FakeNative)

    async with bitmart.private(
        api_key="api-key",
        api_secret="api-secret",
        memo="memo",
        timeout=2,
        base_url="wss://example.test/private",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.memo == "memo"
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/private"
        assert ws.is_logged_in() is True

        await ws.subscribe_orders()
        await ws.subscribe_orders("BTC-USDT-SPOT")
        await ws.subscribe_balance()
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        "spot/user/orders:ALL_SYMBOLS",
        "spot/user/order:BTC-USDT-SPOT",
        "spot/user/balance:BALANCE_UPDATE",
    ]
    assert native_client.ping_count == 1
    assert event == {"event": "subscribe", "topic": "spot/user/balance:BALANCE_UPDATE"}
    assert native_client.closed is True
    assert ws.is_logged_in() is False


@pytest.mark.asyncio
async def test_bitmart_ws_returns_pong(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitmart

    class FakeNativeClient(_FakeNativeBitmartPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"pong"'

    class FakeNative:
        BitmartPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(bitmart, "_native", FakeNative)

    ws = bitmart.public()
    assert await ws.recv() == "pong"
