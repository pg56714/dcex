# ruff: noqa: D100, D103

import pytest


class _FakeNativeBitmexPublicWebSocketClient:
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

    async def subscribe(self, args: list[str]) -> None:
        self.subscriptions.extend(args)

    async def unsubscribe(self, args: list[str]) -> None:
        self.unsubscriptions.extend(args)

    async def subscribe_table(
        self,
        table: str,
        product_symbol: str | None = None,
    ) -> None:
        arg = table if product_symbol is None else f"{table}:{product_symbol}"
        await self.subscribe([arg])

    async def unsubscribe_table(
        self,
        table: str,
        product_symbol: str | None = None,
    ) -> None:
        arg = table if product_symbol is None else f"{table}:{product_symbol}"
        await self.unsubscribe([arg])

    async def subscribe_instrument(self, product_symbol: str) -> None:
        await self.subscribe_table("instrument", product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        await self.subscribe_table("trade", product_symbol)

    async def subscribe_quotes(self, product_symbol: str) -> None:
        await self.subscribe_table("quote", product_symbol)

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 10) -> None:
        table = "orderBook10" if depth == 10 else "orderBookL2"
        await self.subscribe_table(table, product_symbol)

    async def subscribe_klines(self, product_symbol: str, bin_size: str) -> None:
        await self.subscribe_table(f"tradeBin{bin_size}", product_symbol)

    async def recv(self) -> bytes:
        return b'{"table":"trade","action":"partial","data":[]}'


class _FakeNativeBitmexPrivateWebSocketClient:
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
        self.authenticated = False
        self.ping_count = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True
        self.authenticated = True

    async def login(self) -> None:
        self.authenticated = True

    async def close(self) -> None:
        self.closed = True
        self.authenticated = False

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe(self, args: list[str]) -> None:
        self.subscriptions.extend(args)

    async def unsubscribe(self, args: list[str]) -> None:
        self.unsubscriptions.extend(args)

    async def subscribe_orders(self, product_symbol: str) -> None:
        await self.subscribe([f"order:{product_symbol}"])

    async def subscribe_executions(self, product_symbol: str) -> None:
        await self.subscribe([f"execution:{product_symbol}"])

    async def subscribe_positions(self, product_symbol: str) -> None:
        await self.subscribe([f"position:{product_symbol}"])

    async def subscribe_margin(self) -> None:
        await self.subscribe(["margin"])

    async def subscribe_wallet(self) -> None:
        await self.subscribe(["wallet"])

    def is_authenticated(self) -> bool:
        return self.authenticated

    async def recv(self) -> bytes:
        return b'{"table":"margin","action":"partial","data":[]}'


class _FakeNative:
    BitmexPublicWebSocketClient = _FakeNativeBitmexPublicWebSocketClient
    BitmexPrivateWebSocketClient = _FakeNativeBitmexPrivateWebSocketClient


@pytest.mark.asyncio
async def test_bitmex_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitmex

    monkeypatch.setattr(bitmex, "_native", _FakeNative)

    async with bitmex.public(timeout=2, base_url="wss://example.test/realtime") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/realtime"

        await ws.subscribe_trades("XBTUSD")
        await ws.subscribe_quotes("XBTUSD")
        await ws.subscribe_orderbook("XBTUSD")
        await ws.subscribe_klines("XBTUSD", "1m")
        await ws.subscribe_table("instrument", "XBTUSD")
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        "trade:XBTUSD",
        "quote:XBTUSD",
        "orderBook10:XBTUSD",
        "tradeBin1m:XBTUSD",
        "instrument:XBTUSD",
    ]
    assert native_client.ping_count == 1
    assert event == {"table": "trade", "action": "partial", "data": []}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_bitmex_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitmex

    class FakeNativeClient(_FakeNativeBitmexPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        BitmexPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(bitmex, "_native", FakeNative)

    ws = bitmex.public()
    with pytest.raises(RuntimeError, match="Unexpected BitMEX WebSocket event payload"):
        await ws.recv()


@pytest.mark.asyncio
async def test_bitmex_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitmex

    monkeypatch.setattr(bitmex, "_native", _FakeNative)

    async with bitmex.private(
        api_key="api-key",
        api_secret="api-secret",
        timeout=2,
        base_url="wss://example.test/realtime",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/realtime"
        assert ws.is_authenticated() is True

        await ws.subscribe_orders("XBTUSD")
        await ws.subscribe_executions("XBTUSD")
        await ws.subscribe_positions("XBTUSD")
        await ws.subscribe_margin()
        await ws.subscribe_wallet()
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        "order:XBTUSD",
        "execution:XBTUSD",
        "position:XBTUSD",
        "margin",
        "wallet",
    ]
    assert native_client.ping_count == 1
    assert event == {"table": "margin", "action": "partial", "data": []}
    assert native_client.closed is True
    assert ws.is_authenticated() is False
