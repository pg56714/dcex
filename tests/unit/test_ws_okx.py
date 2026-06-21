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


class _FakeNativeOkxPrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.logged_in = False
        self.subscriptions: list[tuple[str, str | None, str | None, str | None]] = []

    async def connect(self) -> None:
        self.connected = True
        self.logged_in = True

    async def login(self) -> None:
        self.logged_in = True

    async def close(self) -> None:
        self.closed = True
        self.logged_in = False

    async def subscribe_channel(
        self,
        channel: str,
        inst_type: str | None = None,
        inst_id: str | None = None,
        ccy: str | None = None,
    ) -> None:
        self.subscriptions.append((channel, inst_type, inst_id, ccy))

    async def unsubscribe_channel(
        self,
        channel: str,
        inst_type: str | None = None,
        inst_id: str | None = None,
        ccy: str | None = None,
    ) -> None:
        self.subscriptions.remove((channel, inst_type, inst_id, ccy))

    async def subscribe_orders(
        self,
        inst_type: str | None = None,
        inst_id: str | None = None,
    ) -> None:
        await self.subscribe_channel("orders", inst_type, inst_id)

    async def subscribe_account(self, ccy: str | None = None) -> None:
        await self.subscribe_channel("account", ccy=ccy)

    async def subscribe_positions(self, inst_type: str | None = None) -> None:
        await self.subscribe_channel("positions", inst_type=inst_type)

    def is_logged_in(self) -> bool:
        return self.logged_in

    async def recv(self) -> bytes:
        return b'{"event":"subscribe","arg":{"channel":"orders","instType":"SWAP"}}'


class _FakeNative:
    OkxPublicWebSocketClient = _FakeNativeOkxPublicWebSocketClient
    OkxPrivateWebSocketClient = _FakeNativeOkxPrivateWebSocketClient


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


@pytest.mark.asyncio
async def test_okx_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import okx

    monkeypatch.setattr(okx, "_native", _FakeNative)

    async with okx.private(
        api_key="api-key",
        api_secret="api-secret",
        passphrase="passphrase",
        timeout=2,
        base_url="wss://example.test/private",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.passphrase == "passphrase"
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/private"
        assert ws.is_logged_in() is True

        await ws.subscribe_orders(inst_type="SWAP")
        await ws.subscribe_account(ccy="USDT")
        event = await ws.recv()

    assert native_client.subscriptions == [
        ("orders", "SWAP", None, None),
        ("account", None, None, "USDT"),
    ]
    assert event == {"event": "subscribe", "arg": {"channel": "orders", "instType": "SWAP"}}
    assert native_client.closed is True
    assert ws.is_logged_in() is False
