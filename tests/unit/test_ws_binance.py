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


class _FakeNativeBinancePrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.spot_http_base_url = spot_http_base_url
        self.futures_http_base_url = futures_http_base_url
        self.ws_base_url = ws_base_url
        self.connected = False
        self.closed = False
        self.keep_alive_count = 0
        self.closed_listen_key = False
        self._listen_key: str | None = None

    async def connect(self) -> str:
        self.connected = True
        self._listen_key = "listen-key"
        return self._listen_key

    async def close(self) -> None:
        self.closed = True
        self._listen_key = None

    async def keep_alive(self) -> None:
        self.keep_alive_count += 1

    async def close_listen_key(self) -> None:
        self.closed_listen_key = True
        self._listen_key = None

    def listen_key(self) -> str | None:
        return self._listen_key

    async def recv(self) -> bytes:
        return b'{"e":"ACCOUNT_UPDATE","E":123}'


class _FakeNativeBinanceEquityWebSocketClient:
    def __init__(
        self,
        stream: str,
        product_symbol: str | None = None,
        interval: str | None = None,
        listen_key: str | None = None,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.stream = stream
        self.product_symbol = product_symbol
        self.interval = interval
        self.listen_key = listen_key
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False

    def url(self) -> str:
        base_url = self.base_url or "wss://nbstream.binance.com/equity"
        symbol = (self.product_symbol or "").split("-", 1)[0]
        return f"{base_url}/ws/{symbol}@{self.stream}"

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def recv(self) -> bytes:
        return b'{"e":"quote","s":"AAPLUSDC"}'


class _FakeNative:
    BinancePublicWebSocketClient = _FakeNativeBinancePublicWebSocketClient
    BinancePrivateWebSocketClient = _FakeNativeBinancePrivateWebSocketClient
    BinanceEquityWebSocketClient = _FakeNativeBinanceEquityWebSocketClient


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


@pytest.mark.asyncio
async def test_binance_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import binance

    monkeypatch.setattr(binance, "_native", _FakeNative)

    async with binance.private(
        api_key="api-key",
        api_secret="api-secret",
        timeout=2,
        futures_http_base_url="https://example.test/fapi",
        ws_base_url="wss://example.test/private",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.timeout == 2
        assert native_client.futures_http_base_url == "https://example.test/fapi"
        assert native_client.ws_base_url == "wss://example.test/private"
        assert ws.listen_key() == "listen-key"

        await ws.keep_alive()
        event = await ws.recv()

    assert event == {"e": "ACCOUNT_UPDATE", "E": 123}
    assert native_client.keep_alive_count == 1
    assert native_client.closed is True
    assert ws.listen_key() is None


@pytest.mark.asyncio
async def test_binance_equity_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import binance

    monkeypatch.setattr(binance, "_native", _FakeNative)

    async with binance.equity(
        stream="quote",
        product_symbol="AAPL-USDC-EQUITY",
        timeout=2,
        base_url="wss://example.test/equity",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.stream == "quote"
        assert native_client.product_symbol == "AAPL-USDC-EQUITY"
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/equity"
        assert ws.url == "wss://example.test/equity/ws/AAPL@quote"

        event = await ws.recv()

    assert event == {"e": "quote", "s": "AAPLUSDC"}
    assert native_client.closed is True
