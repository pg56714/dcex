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


class _RecordingNativeOkxPublicWebSocketClient(_FakeNativeOkxPublicWebSocketClient):
    def __init__(self, timeout: float = 10.0, base_url: str | None = None) -> None:
        super().__init__(timeout=timeout, base_url=base_url)
        self.calls: list[tuple[str, tuple[str | None, ...]]] = []

    async def subscribe_channel(self, *args: str | None, **kwargs: str) -> None:  # type: ignore[override]
        self.calls.append(("subscribe", args + tuple(kwargs.items())))

    async def unsubscribe_channel(self, *args: str | None, **kwargs: str) -> None:  # type: ignore[override]
        self.calls.append(("unsubscribe", args + tuple(kwargs.items())))


class _RecordingNativeOkxPrivateWebSocketClient(_FakeNativeOkxPrivateWebSocketClient):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.calls: list[tuple[str, tuple[str | None, ...]]] = []

    async def subscribe_channel(self, *args: str | None, **kwargs: str) -> None:  # type: ignore[override]
        self.calls.append(("subscribe_channel", args + tuple(kwargs.items())))

    async def unsubscribe_channel(self, *args: str | None, **kwargs: str) -> None:  # type: ignore[override]
        self.calls.append(("unsubscribe_channel", args + tuple(kwargs.items())))

    async def subscribe_orders(self, *args: str | None) -> None:  # type: ignore[override]
        self.calls.append(("subscribe_orders", args))


class _RecordingNative:
    OkxPublicWebSocketClient = _RecordingNativeOkxPublicWebSocketClient
    OkxPrivateWebSocketClient = _RecordingNativeOkxPrivateWebSocketClient


@pytest.mark.asyncio
async def test_okx_public_ws_forwards_inst_type_and_inst_family(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import okx

    monkeypatch.setattr(okx, "_native", _RecordingNative)

    ws = okx.public()
    await ws.subscribe_channel("trades", "BTC-USDT-SPOT")
    await ws.subscribe_channel("instruments", inst_type="SPOT")
    await ws.subscribe_channel("opt-summary", inst_family="BTC-USD")
    await ws.subscribe_channel("option-trades", inst_type="OPTION", inst_family="BTC-USD")
    await ws.subscribe_channel("estimated-price", "BTC-USD-SWAP", inst_type="SWAP")
    await ws.unsubscribe_channel("liquidation-orders", inst_type="SWAP")
    await ws.unsubscribe_channel("trades", "BTC-USDT-SPOT")

    assert ws._native_client.calls == [
        # Unfiltered calls keep the legacy two-argument native signature.
        ("subscribe", ("trades", "BTC-USDT-SPOT")),
        ("subscribe", ("instruments", None, "SPOT", None)),
        ("subscribe", ("opt-summary", None, None, "BTC-USD")),
        ("subscribe", ("option-trades", None, "OPTION", "BTC-USD")),
        ("subscribe", ("estimated-price", "BTC-USD-SWAP", "SWAP", None)),
        ("unsubscribe", ("liquidation-orders", None, "SWAP", None)),
        ("unsubscribe", ("trades", "BTC-USDT-SPOT")),
    ]


@pytest.mark.asyncio
async def test_okx_private_ws_forwards_inst_family(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import okx

    monkeypatch.setattr(okx, "_native", _RecordingNative)

    ws = okx.private(api_key="k", api_secret="s", passphrase="p")
    await ws.subscribe_orders(inst_type="SWAP")
    await ws.subscribe_orders(inst_type="SWAP", inst_family="BTC-USDT")
    await ws.subscribe_orders(inst_family="BTC-USD")
    await ws.subscribe_channel("positions", "FUTURES", inst_family="BTC-USD")
    await ws.subscribe_channel("deposit-info", ccy="BTC")
    await ws.unsubscribe_channel("orders-algo", "SWAP", inst_family="BTC-USDT")

    assert ws._native_client.calls == [
        ("subscribe_orders", ("SWAP", None)),
        ("subscribe_orders", ("SWAP", None, "BTC-USDT")),
        ("subscribe_orders", (None, None, "BTC-USD")),
        ("subscribe_channel", ("positions", "FUTURES", None, None, "BTC-USD")),
        ("subscribe_channel", ("deposit-info", None, None, "BTC")),
        ("unsubscribe_channel", ("orders-algo", "SWAP", None, None, "BTC-USDT")),
    ]


def test_okx_native_ws_clients_accept_inst_filters() -> None:
    """Requires a native extension rebuilt from crates/dcex-python."""
    native = pytest.importorskip("dcex._native")

    public_sig = native.OkxPublicWebSocketClient.subscribe_channel.__text_signature__
    private_sig = native.OkxPrivateWebSocketClient.subscribe_channel.__text_signature__
    orders_sig = native.OkxPrivateWebSocketClient.subscribe_orders.__text_signature__

    assert "inst_type=None" in public_sig
    assert "inst_family=None" in public_sig
    assert "inst_family=None" in private_sig
    assert "inst_family=None" in orders_sig
    assert "sprd_id=None" in public_sig
    assert "sprd_id=None" in private_sig


@pytest.mark.asyncio
async def test_okx_ws_forwards_sprd_id_only_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import okx

    monkeypatch.setattr(okx, "_native", _RecordingNative)

    sprd = "BTC-USDT_BTC-USDT-SWAP"
    public_ws = okx.public()
    await public_ws.subscribe_channel("sprd-books5", sprd_id=sprd)
    await public_ws.unsubscribe_channel("sprd-tickers", sprd_id=sprd)
    await public_ws.subscribe_channel("instruments", inst_type="SPOT")

    private_ws = okx.private(api_key="k", api_secret="s", passphrase="p")
    await private_ws.subscribe_channel("sprd-orders", sprd_id=sprd)
    await private_ws.unsubscribe_channel("sprd-trades", sprd_id=sprd)
    await private_ws.subscribe_channel("orders", "SWAP")

    assert public_ws._native_client.calls == [
        ("subscribe", ("sprd-books5", None, None, None, ("sprd_id", sprd))),
        ("unsubscribe", ("sprd-tickers", None, None, None, ("sprd_id", sprd))),
        ("subscribe", ("instruments", None, "SPOT", None)),
    ]
    assert private_ws._native_client.calls == [
        ("subscribe_channel", ("sprd-orders", None, None, None, None, ("sprd_id", sprd))),
        ("unsubscribe_channel", ("sprd-trades", None, None, None, None, ("sprd_id", sprd))),
        ("subscribe_channel", ("orders", "SWAP", None, None)),
    ]
