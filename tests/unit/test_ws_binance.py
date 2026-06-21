# ruff: noqa: D100, D103

import pytest


class _FakeNativeBinancePublicWebSocketClient:
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.streams: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def subscribe(self, streams: list[str]) -> int:
        self.streams.extend(streams)
        return 1

    async def unsubscribe(self, streams: list[str]) -> int:
        self.streams = [stream for stream in self.streams if stream not in streams]
        return 2

    async def subscribe_trades(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:trade")
        return 3

    async def subscribe_agg_trades(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:aggTrade")
        return 4

    async def subscribe_orderbook(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:depth")
        return 5

    async def subscribe_ticker(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:ticker")
        return 6

    async def subscribe_klines(self, product_symbol: str, interval: str) -> int:
        self.streams.append(f"{product_symbol}:kline_{interval}")
        return 7

    async def recv(self) -> bytes:
        return b'{"e":"trade","s":"BTCUSDT"}'


class _FakeNative:
    BinancePublicWebSocketClient = _FakeNativeBinancePublicWebSocketClient


@pytest.mark.asyncio
async def test_binance_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import binance

    monkeypatch.setattr(binance, "_native", _FakeNative)

    async with binance.public(timeout=2, base_url="wss://example.test/ws") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        assert await ws.subscribe_trades("BTC-USDT-SPOT") == 3
        assert await ws.subscribe_klines("BTC-USDT-SPOT", "1m") == 7
        event = await ws.recv()

    assert event == {"e": "trade", "s": "BTCUSDT"}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_binance_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import binance

    class FakeNativeClient(_FakeNativeBinancePublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        BinancePublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(binance, "_native", FakeNative)

    ws = binance.public()
    with pytest.raises(RuntimeError, match="Unexpected Binance WebSocket event payload"):
        await ws.recv()
