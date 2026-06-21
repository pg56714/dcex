# ruff: noqa: D100, D103

import pytest


class _FakeNativeKrakenPublicWebSocketClient:
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.subscriptions: list[tuple[str, list[str]]] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> int:
        return 1

    async def subscribe_channel(self, channel: str, product_symbols: list[str]) -> int:
        self.subscriptions.append((channel, product_symbols))
        return 2

    async def unsubscribe_channel(self, channel: str, product_symbols: list[str]) -> int:
        self.subscriptions.remove((channel, product_symbols))
        return 3

    async def subscribe_ticker(self, product_symbol: str) -> int:
        self.subscriptions.append(("ticker", [product_symbol]))
        return 4

    async def subscribe_trades(self, product_symbol: str) -> int:
        self.subscriptions.append(("trade", [product_symbol]))
        return 5

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 10) -> int:
        self.subscriptions.append((f"book:{depth}", [product_symbol]))
        return 6

    async def subscribe_klines(self, product_symbol: str, interval: int = 1) -> int:
        self.subscriptions.append((f"ohlc:{interval}", [product_symbol]))
        return 7

    async def recv(self) -> bytes:
        return b'{"channel":"trade","type":"snapshot","data":[]}'


class _FakeNativeKrakenPrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.spot_http_base_url = spot_http_base_url
        self.ws_base_url = ws_base_url
        self.connected = False
        self.closed = False
        self.current_token: str | None = None
        self.subscriptions: list[str] = []

    async def connect(self) -> str:
        self.connected = True
        self.current_token = "token-value"
        return "token-value"

    async def fetch_token(self) -> str:
        self.current_token = "token-value"
        return "token-value"

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> int:
        return 8

    async def subscribe_balances(self) -> int:
        self.subscriptions.append("balances")
        return 9

    async def unsubscribe_balances(self) -> int:
        self.subscriptions.remove("balances")
        return 10

    async def subscribe_executions(
        self,
        snap_orders: bool = True,
        snap_trades: bool = False,
    ) -> int:
        self.subscriptions.append(f"executions:{snap_orders}:{snap_trades}")
        return 11

    async def unsubscribe_executions(self) -> int:
        self.subscriptions = [
            subscription
            for subscription in self.subscriptions
            if not subscription.startswith("executions:")
        ]
        return 12

    def token(self) -> str | None:
        return self.current_token

    async def recv(self) -> bytes:
        return b'{"channel":"balances","type":"snapshot","data":[]}'


class _FakeNative:
    KrakenPublicWebSocketClient = _FakeNativeKrakenPublicWebSocketClient
    KrakenPrivateWebSocketClient = _FakeNativeKrakenPrivateWebSocketClient


@pytest.mark.asyncio
async def test_kraken_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import kraken

    monkeypatch.setattr(kraken, "_native", _FakeNative)

    async with kraken.public(timeout=2, base_url="wss://example.test/ws") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        assert await ws.subscribe_trades("BTC-USD-SPOT") == 5
        assert await ws.subscribe_orderbook("BTC-USD-SPOT", depth=25) == 6
        assert await ws.subscribe_klines("BTC-USD-SPOT", interval=5) == 7
        assert await ws.ping() == 1
        event = await ws.recv()

    assert native_client.subscriptions == [
        ("trade", ["BTC-USD-SPOT"]),
        ("book:25", ["BTC-USD-SPOT"]),
        ("ohlc:5", ["BTC-USD-SPOT"]),
    ]
    assert event == {"channel": "trade", "type": "snapshot", "data": []}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_kraken_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import kraken

    monkeypatch.setattr(kraken, "_native", _FakeNative)

    async with kraken.private(
        api_key="api-key",
        api_secret="api-secret",
        timeout=2,
        spot_http_base_url="https://example.test",
        ws_base_url="wss://example.test/private",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.timeout == 2
        assert native_client.spot_http_base_url == "https://example.test"
        assert native_client.ws_base_url == "wss://example.test/private"
        assert ws.token() == "token-value"

        assert await ws.subscribe_balances() == 9
        assert await ws.subscribe_executions(snap_orders=True, snap_trades=True) == 11
        assert await ws.ping() == 8
        event = await ws.recv()

    assert native_client.subscriptions == ["balances", "executions:True:True"]
    assert event == {"channel": "balances", "type": "snapshot", "data": []}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_kraken_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import kraken

    class FakeNativeClient(_FakeNativeKrakenPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        KrakenPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(kraken, "_native", FakeNative)

    ws = kraken.public()
    with pytest.raises(RuntimeError, match="Unexpected Kraken WebSocket event payload"):
        await ws.recv()
