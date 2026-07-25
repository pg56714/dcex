# ruff: noqa: D100, D103

import pytest


class _FakeNativeMexcPublicWebSocketClient:
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.ping_count = 0
        self.subscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.ping_count += 1

    async def subscribe(self, channels: list[str]) -> None:
        self.subscriptions.extend(channels)

    async def unsubscribe(self, channels: list[str]) -> None:
        self.subscriptions = [channel for channel in self.subscriptions if channel not in channels]

    async def subscribe_trades(self, product_symbol: str, speed: str = "100ms") -> None:
        self.subscriptions.append(f"trades:{speed}:{product_symbol}")

    async def subscribe_orderbook(self, product_symbol: str, speed: str = "100ms") -> None:
        self.subscriptions.append(f"depth:{speed}:{product_symbol}")

    async def subscribe_partial_orderbook(
        self,
        product_symbol: str,
        levels: int = 5,
    ) -> None:
        self.subscriptions.append(f"partial:{levels}:{product_symbol}")

    async def subscribe_book_ticker(self, product_symbol: str, speed: str = "100ms") -> None:
        self.subscriptions.append(f"bookTicker:{speed}:{product_symbol}")

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        self.subscriptions.append(f"kline:{interval}:{product_symbol}")

    async def recv(self) -> bytes:
        return b'{"id":0,"code":0,"msg":"PONG"}'


class _FakeNativeMexcPrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str | None = None,
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
        self.current_listen_key: str | None = None
        self.subscriptions: list[str] = []

    async def connect(self) -> str:
        self.connected = True
        self.current_listen_key = "listen-key"
        return "listen-key"

    async def keep_alive(self) -> str:
        return self.current_listen_key or "listen-key"

    async def close_listen_key(self) -> None:
        self.current_listen_key = None

    async def close(self) -> None:
        self.closed = True
        self.current_listen_key = None

    async def ping(self) -> None:
        return None

    async def subscribe(self, channels: list[str]) -> None:
        self.subscriptions.extend(channels)

    async def unsubscribe(self, channels: list[str]) -> None:
        self.subscriptions = [channel for channel in self.subscriptions if channel not in channels]

    async def subscribe_account(self) -> None:
        self.subscriptions.append("spot@private.account.v3.api.pb")

    async def subscribe_deals(self) -> None:
        self.subscriptions.append("spot@private.deals.v3.api.pb")

    async def subscribe_orders(self) -> None:
        self.subscriptions.append("spot@private.orders.v3.api.pb")

    def listen_key(self) -> str | None:
        return self.current_listen_key

    async def recv(self) -> bytes:
        return b"\x08\x96\x01"


class _FakeNative:
    MexcPublicWebSocketClient = _FakeNativeMexcPublicWebSocketClient
    MexcPrivateWebSocketClient = _FakeNativeMexcPrivateWebSocketClient


@pytest.mark.asyncio
async def test_mexc_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import mexc

    monkeypatch.setattr(mexc, "_native", _FakeNative)

    async with mexc.public(timeout=2, base_url="wss://example.test/ws") as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        await ws.subscribe_trades("BTC-USDT-SPOT", speed="10ms")
        await ws.subscribe_orderbook("BTC-USDT-SPOT", speed="10ms")
        await ws.subscribe_partial_orderbook("BTC-USDT-SPOT", levels=20)
        await ws.subscribe_book_ticker("BTC-USDT-SPOT", speed="10ms")
        await ws.subscribe_klines("BTC-USDT-SPOT", "Min1")
        await ws.ping()
        event = await ws.recv()

    assert native_client.subscriptions == [
        "trades:10ms:BTC-USDT-SPOT",
        "depth:10ms:BTC-USDT-SPOT",
        "partial:20:BTC-USDT-SPOT",
        "bookTicker:10ms:BTC-USDT-SPOT",
        "kline:Min1:BTC-USDT-SPOT",
    ]
    assert native_client.ping_count == 1
    assert event == {"id": 0, "code": 0, "msg": "PONG"}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_mexc_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import mexc

    monkeypatch.setattr(mexc, "_native", _FakeNative)

    async with mexc.private(
        api_key="api-key",
        api_secret="api-secret",
        timeout=2,
        spot_http_base_url="https://example.test",
        ws_base_url="wss://example.test/ws",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.timeout == 2
        assert native_client.spot_http_base_url == "https://example.test"
        assert native_client.ws_base_url == "wss://example.test/ws"
        assert ws.listen_key() == "listen-key"

        await ws.subscribe_account()
        await ws.subscribe_deals()
        await ws.subscribe_orders()
        assert await ws.keep_alive() == "listen-key"
        event = await ws.recv()

    assert native_client.subscriptions == [
        "spot@private.account.v3.api.pb",
        "spot@private.deals.v3.api.pb",
        "spot@private.orders.v3.api.pb",
    ]
    assert event == b"\x08\x96\x01"
    assert native_client.closed is True
    assert ws.listen_key() is None


@pytest.mark.asyncio
async def test_mexc_ws_rejects_unexpected_json_scalar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import mexc

    class FakeNativeClient(_FakeNativeMexcPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        MexcPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(mexc, "_native", FakeNative)

    ws = mexc.public()
    with pytest.raises(RuntimeError, match="Unexpected MEXC WebSocket event payload"):
        await ws.recv()
