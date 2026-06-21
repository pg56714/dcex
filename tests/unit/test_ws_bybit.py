# ruff: noqa: D100, D103

import pytest


class _FakeNativeBybitPublicWebSocketClient:
    def __init__(
        self,
        category: str = "linear",
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.category = category
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.topics: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def subscribe(self, topics: list[str]) -> str:
        self.topics.extend(topics)
        return "1"

    async def unsubscribe(self, topics: list[str]) -> str:
        self.topics = [topic for topic in self.topics if topic not in topics]
        return "2"

    async def ping(self) -> str:
        return "3"

    async def subscribe_trades(self, product_symbol: str) -> str:
        self.topics.append(f"publicTrade.{product_symbol}")
        return "4"

    async def subscribe_ticker(self, product_symbol: str) -> str:
        self.topics.append(f"tickers.{product_symbol}")
        return "5"

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 1) -> str:
        self.topics.append(f"orderbook.{depth}.{product_symbol}")
        return "6"

    async def subscribe_klines(self, product_symbol: str, interval: str) -> str:
        self.topics.append(f"kline.{interval}.{product_symbol}")
        return "7"

    async def recv(self) -> bytes:
        return b'{"topic":"publicTrade.BTCUSDT","type":"snapshot"}'


class _FakeNative:
    BybitPublicWebSocketClient = _FakeNativeBybitPublicWebSocketClient


@pytest.mark.asyncio
async def test_bybit_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bybit

    monkeypatch.setattr(bybit, "_native", _FakeNative)

    async with bybit.public(category="spot", timeout=2, base_url="wss://example.test/ws") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.category == "spot"
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        assert await ws.subscribe_trades("BTC-USDT-SPOT") == "4"
        assert await ws.subscribe_orderbook("BTC-USDT-SPOT", depth=50) == "6"
        assert await ws.ping() == "3"
        event = await ws.recv()

    assert native_client.topics == [
        "publicTrade.BTC-USDT-SPOT",
        "orderbook.50.BTC-USDT-SPOT",
    ]
    assert event == {"topic": "publicTrade.BTCUSDT", "type": "snapshot"}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_bybit_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bybit

    class FakeNativeClient(_FakeNativeBybitPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        BybitPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(bybit, "_native", FakeNative)

    ws = bybit.public()
    with pytest.raises(RuntimeError, match="Unexpected Bybit WebSocket event payload"):
        await ws.recv()
