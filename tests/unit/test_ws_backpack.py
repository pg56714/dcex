# ruff: noqa: D100, D103

import pytest


class _FakeNativeBackpackPublicWebSocketClient:
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.pings = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.pings += 1

    async def subscribe(self, streams: list[str]) -> None:
        self.subscriptions.extend(streams)

    async def unsubscribe(self, streams: list[str]) -> None:
        self.unsubscriptions.extend(streams)

    async def subscribe_book_ticker(self, product_symbol: str) -> None:
        await self.subscribe([f"bookTicker.{product_symbol}"])

    async def subscribe_depth(
        self,
        product_symbol: str,
        speed: str | None = None,
    ) -> None:
        stream = f"depth.{speed}.{product_symbol}" if speed else f"depth.{product_symbol}"
        await self.subscribe([stream])

    async def subscribe_orderbook(
        self,
        product_symbol: str,
        speed: str | None = None,
    ) -> None:
        await self.subscribe_depth(product_symbol, speed)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        await self.subscribe([f"kline.{interval}.{product_symbol}"])

    async def subscribe_liquidation(self, product_symbol: str) -> None:
        await self.subscribe([f"liquidation.{product_symbol}"])

    async def subscribe_mark_price(self, product_symbol: str) -> None:
        await self.subscribe([f"markPrice.{product_symbol}"])

    async def subscribe_ticker(self, product_symbol: str) -> None:
        await self.subscribe([f"ticker.{product_symbol}"])

    async def subscribe_open_interest(self, product_symbol: str) -> None:
        await self.subscribe([f"openInterest.{product_symbol}"])

    async def subscribe_trades(self, product_symbol: str) -> None:
        await self.subscribe([f"trade.{product_symbol}"])

    async def recv(self) -> bytes:
        return b'{"stream":"trade.SOL_USDC","data":{"e":"trade"}}'


class _FakeNativeBackpackPrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        window: int = 5000,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.window = window
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.pings = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.pings += 1

    async def subscribe(self, streams: list[str]) -> None:
        self.subscriptions.extend(streams)

    async def unsubscribe(self, streams: list[str]) -> None:
        self.unsubscriptions.extend(streams)

    async def subscribe_orders(self, product_symbol: str | None = None) -> None:
        stream = "account.orderUpdate"
        if product_symbol is not None:
            stream = f"{stream}.{product_symbol}"
        await self.subscribe([stream])

    async def subscribe_positions(self, product_symbol: str | None = None) -> None:
        stream = "account.positionUpdate"
        if product_symbol is not None:
            stream = f"{stream}.{product_symbol}"
        await self.subscribe([stream])

    async def subscribe_rfq(self, product_symbol: str | None = None) -> None:
        stream = "account.rfqUpdate"
        if product_symbol is not None:
            stream = f"{stream}.{product_symbol}"
        await self.subscribe([stream])

    async def recv(self) -> bytes:
        return b'{"stream":"account.orderUpdate","data":{"e":"orderAccepted"}}'


class _FakeNative:
    BackpackPublicWebSocketClient = _FakeNativeBackpackPublicWebSocketClient
    BackpackPrivateWebSocketClient = _FakeNativeBackpackPrivateWebSocketClient


@pytest.mark.asyncio
async def test_backpack_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import backpack

    monkeypatch.setattr(backpack, "_native", _FakeNative)

    async with backpack.public(timeout=2, base_url="wss://example.test") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test"

        await ws.ping()
        await ws.subscribe_trades("SOL_USDC")
        await ws.subscribe_orderbook("SOL_USDC", speed="200ms")
        await ws.subscribe_klines("SOL_USDC", "1m")
        await ws.subscribe_liquidation("SOL_USDC_PERP")
        event = await ws.recv()

    assert native_client.pings == 1
    assert native_client.subscriptions == [
        "trade.SOL_USDC",
        "depth.200ms.SOL_USDC",
        "kline.1m.SOL_USDC",
        "liquidation.SOL_USDC_PERP",
    ]
    assert event == {"stream": "trade.SOL_USDC", "data": {"e": "trade"}}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_backpack_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import backpack

    monkeypatch.setattr(backpack, "_native", _FakeNative)

    async with backpack.private(
        api_key="api-key",
        api_secret="api-secret",
        window=6000,
        timeout=2,
        base_url="wss://example.test",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.window == 6000
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test"

        await ws.ping()
        await ws.subscribe_orders()
        await ws.subscribe_positions("SOL_USDC_PERP")
        event = await ws.recv()

    assert native_client.pings == 1
    assert native_client.subscriptions == [
        "account.orderUpdate",
        "account.positionUpdate.SOL_USDC_PERP",
    ]
    assert event == {"stream": "account.orderUpdate", "data": {"e": "orderAccepted"}}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_backpack_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import backpack

    class FakeNativeClient(_FakeNativeBackpackPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        BackpackPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(backpack, "_native", FakeNative)

    ws = backpack.public()
    with pytest.raises(RuntimeError, match="Unexpected Backpack WebSocket event payload"):
        await ws.recv()
