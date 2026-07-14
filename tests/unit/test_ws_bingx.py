# ruff: noqa: D100, D103

import pytest


class _FakeNativeBingxPublicWebSocketClient:
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.ping_count = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe(self, data_type: str) -> str:
        self.subscriptions.append(data_type)
        return "sub-1"

    async def unsubscribe(self, data_type: str) -> str:
        self.unsubscriptions.append(data_type)
        return "unsub-1"

    async def subscribe_ticker(self, product_symbol: str) -> str:
        symbol = product_symbol.removesuffix("-SPOT")
        return await self.subscribe(f"{symbol}@ticker")

    async def subscribe_trades(self, product_symbol: str) -> str:
        symbol = product_symbol.removesuffix("-SPOT")
        return await self.subscribe(f"{symbol}@trade")

    async def subscribe_orderbook(
        self,
        product_symbol: str,
        depth: int = 5,
        speed: str = "500ms",
    ) -> str:
        _ = speed
        symbol = product_symbol.removesuffix("-SPOT")
        return await self.subscribe(f"{symbol}@depth{depth}")

    async def subscribe_klines(self, product_symbol: str, interval: str) -> str:
        symbol = product_symbol.removesuffix("-SPOT")
        interval = {"1m": "1min", "3m": "3min", "5m": "5min"}.get(interval, interval)
        return await self.subscribe(f"{symbol}@kline_{interval}")

    async def recv(self) -> bytes:
        return b'{"code":0,"dataType":"BTC-USDT@trade","data":[]}'


class _FakeNativeBingxPrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.http_base_url = http_base_url
        self.ws_base_url = ws_base_url
        self.connected = False
        self.closed = False
        self.ping_count = 0
        self.keep_alive_count = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []
        self._listen_key: str | None = None

    async def connect(self) -> str:
        self.connected = True
        self._listen_key = "listen-key"
        return self._listen_key

    async def connect_with_listen_key(self, listen_key: str) -> None:
        self.connected = True
        self._listen_key = listen_key

    async def keep_alive(self) -> str:
        self.keep_alive_count += 1
        return self._listen_key or "listen-key"

    async def close(self) -> None:
        self.closed = True
        self._listen_key = None

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe(self, data_type: str) -> str:
        self.subscriptions.append(data_type)
        return "sub-1"

    async def unsubscribe(self, data_type: str) -> str:
        self.unsubscriptions.append(data_type)
        return "unsub-1"

    async def subscribe_orders(self) -> str:
        return await self.subscribe("spot.executionReport")

    def listen_key(self) -> str | None:
        return self._listen_key

    async def recv(self) -> bytes:
        return b'{"code":0,"dataType":"spot.executionReport","data":{}}'


class _FakeNative:
    BingxPublicWebSocketClient = _FakeNativeBingxPublicWebSocketClient
    BingxPrivateWebSocketClient = _FakeNativeBingxPrivateWebSocketClient


@pytest.mark.asyncio
async def test_bingx_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bingx

    monkeypatch.setattr(bingx, "_native", _FakeNative)

    async with bingx.public(timeout=2, base_url="wss://example.test/ws") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        assert await ws.subscribe_trades("BTC-USDT-SPOT") == "sub-1"
        assert await ws.subscribe_ticker("BTC-USDT-SPOT") == "sub-1"
        assert await ws.subscribe_orderbook("BTC-USDT-SPOT") == "sub-1"
        assert await ws.subscribe_klines("BTC-USDT-SPOT", "1m") == "sub-1"
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        "BTC-USDT@trade",
        "BTC-USDT@ticker",
        "BTC-USDT@depth5",
        "BTC-USDT@kline_1min",
    ]
    assert native_client.ping_count == 1
    assert event == {"code": 0, "dataType": "BTC-USDT@trade", "data": []}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_bingx_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bingx

    class FakeNativeClient(_FakeNativeBingxPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b"1"

    class FakeNative:
        BingxPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(bingx, "_native", FakeNative)

    ws = bingx.public()
    with pytest.raises(RuntimeError, match="Unexpected BingX WebSocket event payload"):
        await ws.recv()


@pytest.mark.asyncio
async def test_bingx_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bingx

    monkeypatch.setattr(bingx, "_native", _FakeNative)

    async with bingx.private(
        api_key="api-key",
        api_secret="api-secret",
        timeout=2,
        http_base_url="https://example.test/api",
        ws_base_url="wss://example.test/ws",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.timeout == 2
        assert native_client.http_base_url == "https://example.test/api"
        assert native_client.ws_base_url == "wss://example.test/ws"
        assert ws.listen_key() == "listen-key"

        assert await ws.keep_alive() == "listen-key"
        assert await ws.subscribe_orders() == "sub-1"
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == ["spot.executionReport"]
    assert native_client.keep_alive_count == 1
    assert native_client.ping_count == 1
    assert event == {"code": 0, "dataType": "spot.executionReport", "data": {}}
    assert native_client.closed is True
    assert ws.listen_key() is None
