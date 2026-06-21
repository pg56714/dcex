# ruff: noqa: D100, D103

import pytest


class _FakeNativeOkxPublicWebSocketClient:
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.subscriptions: list[tuple[str, str | None]] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def subscribe_channel(self, channel: str, product_symbol: str | None = None) -> None:
        self.subscriptions.append((channel, product_symbol))

    async def unsubscribe_channel(self, channel: str, product_symbol: str | None = None) -> None:
        self.subscriptions.remove((channel, product_symbol))

    async def subscribe_trades(self, product_symbol: str) -> None:
        await self.subscribe_channel("trades", product_symbol)

    async def subscribe_ticker(self, product_symbol: str) -> None:
        await self.subscribe_channel("tickers", product_symbol)

    async def subscribe_orderbook(self, product_symbol: str) -> None:
        await self.subscribe_channel("books", product_symbol)

    async def subscribe_orderbook5(self, product_symbol: str) -> None:
        await self.subscribe_channel("books5", product_symbol)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        await self.subscribe_channel(f"candle{interval}", product_symbol)

    async def recv(self) -> bytes:
        return b'{"event":"subscribe","arg":{"channel":"trades","instId":"BTC-USDT"}}'


class _FakeNative:
    OkxPublicWebSocketClient = _FakeNativeOkxPublicWebSocketClient


@pytest.mark.asyncio
async def test_okx_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import okx

    monkeypatch.setattr(okx, "_native", _FakeNative)

    async with okx.public(timeout=2, base_url="wss://example.test/ws") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        await ws.subscribe_trades("BTC-USDT-SPOT")
        await ws.subscribe_klines("BTC-USDT-SPOT", "1m")
        event = await ws.recv()

    assert native_client.subscriptions == [
        ("trades", "BTC-USDT-SPOT"),
        ("candle1m", "BTC-USDT-SPOT"),
    ]
    assert event == {"event": "subscribe", "arg": {"channel": "trades", "instId": "BTC-USDT"}}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_okx_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import okx

    class FakeNativeClient(_FakeNativeOkxPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        OkxPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(okx, "_native", FakeNative)

    ws = okx.public()
    with pytest.raises(RuntimeError, match="Unexpected OKX WebSocket event payload"):
        await ws.recv()
