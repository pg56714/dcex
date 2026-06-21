# ruff: noqa: D100, D103

import pytest


class _FakeNativeBitgetPublicWebSocketClient:
    def __init__(
        self,
        inst_type: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.inst_type = inst_type
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.ping_count = 0
        self.subscriptions: list[tuple[str, str]] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe_channel(self, channel: str, product_symbol: str) -> None:
        self.subscriptions.append((channel, product_symbol))

    async def unsubscribe_channel(self, channel: str, product_symbol: str) -> None:
        self.subscriptions.remove((channel, product_symbol))

    async def subscribe_ticker(self, product_symbol: str) -> None:
        await self.subscribe_channel("ticker", product_symbol)

    async def subscribe_trades(self, product_symbol: str) -> None:
        await self.subscribe_channel("trade", product_symbol)

    async def subscribe_orderbook(self, product_symbol: str, depth: int = 5) -> None:
        await self.subscribe_channel(f"books{depth}", product_symbol)

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        await self.subscribe_channel(f"candle{interval}", product_symbol)

    async def recv(self) -> bytes:
        return (
            b'{"event":"subscribe",'
            b'"arg":{"instType":"SPOT","channel":"trade","instId":"BTCUSDT"}}'
        )


class _FakeNative:
    BitgetPublicWebSocketClient = _FakeNativeBitgetPublicWebSocketClient


@pytest.mark.asyncio
async def test_bitget_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitget

    monkeypatch.setattr(bitget, "_native", _FakeNative)

    async with bitget.public(
        inst_type="USDT-FUTURES",
        timeout=2,
        base_url="wss://example.test/ws",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.inst_type == "USDT-FUTURES"
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        await ws.subscribe_trades("BTC-USDT-SPOT")
        await ws.subscribe_orderbook("BTC-USDT-SPOT", depth=15)
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        ("trade", "BTC-USDT-SPOT"),
        ("books15", "BTC-USDT-SPOT"),
    ]
    assert native_client.ping_count == 1
    assert event == {
        "event": "subscribe",
        "arg": {"instType": "SPOT", "channel": "trade", "instId": "BTCUSDT"},
    }
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_bitget_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import bitget

    class FakeNativeClient(_FakeNativeBitgetPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        BitgetPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(bitget, "_native", FakeNative)

    ws = bitget.public()
    with pytest.raises(RuntimeError, match="Unexpected Bitget WebSocket event payload"):
        await ws.recv()
