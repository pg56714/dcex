# ruff: noqa: D100, D103

import pytest


class _FakeNativeKucoinPublicWebSocketClient:
    def __init__(
        self,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        market: str = "spot",
    ) -> None:
        self.timeout = timeout
        self.spot_http_base_url = spot_http_base_url
        self.futures_http_base_url = futures_http_base_url
        self.market = market
        self.connected = False
        self.closed = False
        self.ping_count = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> str:
        self.ping_count += 1
        return "ping-1"

    async def subscribe(self, topic: str) -> str:
        self.subscriptions.append(topic)
        return "sub-1"

    async def unsubscribe(self, topic: str) -> str:
        self.unsubscriptions.append(topic)
        return "unsub-1"

    async def subscribe_ticker(self, product_symbol: str) -> str:
        topic = (
            f"/contractMarket/tickerV2:{product_symbol}"
            if self.market == "futures"
            else f"/market/ticker:{product_symbol}"
        )
        return await self.subscribe(topic)

    async def subscribe_trades(self, product_symbol: str) -> str:
        prefix = "/contractMarket/execution" if self.market == "futures" else "/market/match"
        return await self.subscribe(f"{prefix}:{product_symbol}")

    async def subscribe_orderbook(self, product_symbol: str) -> str:
        prefix = "/contractMarket/level2" if self.market == "futures" else "/market/level2"
        return await self.subscribe(f"{prefix}:{product_symbol}")

    async def subscribe_klines(self, product_symbol: str, interval: str) -> str:
        prefix = "/contractMarket/limitCandle" if self.market == "futures" else "/market/candles"
        return await self.subscribe(f"{prefix}:{product_symbol}_{interval}")

    async def recv(self) -> bytes:
        return b'{"type":"message","topic":"/market/match:BTC-USDT","data":{}}'


class _FakeNativeKucoinPrivateWebSocketClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        market: str = "spot",
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.timeout = timeout
        self.spot_http_base_url = spot_http_base_url
        self.futures_http_base_url = futures_http_base_url
        self.connected = False
        self.closed = False
        self.market = market
        self.ping_count = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> str:
        self.ping_count += 1
        return "ping-1"

    async def subscribe(self, topic: str) -> str:
        self.subscriptions.append(topic)
        return "sub-1"

    async def unsubscribe(self, topic: str) -> str:
        self.unsubscriptions.append(topic)
        return "unsub-1"

    async def subscribe_orders(self) -> str:
        topic = (
            "/contractMarket/tradeOrders" if self.market == "futures" else "/spotMarket/tradeOrders"
        )
        return await self.subscribe(topic)

    async def subscribe_balances(self) -> str:
        topic = "/contractAccount/wallet" if self.market == "futures" else "/account/balance"
        return await self.subscribe(topic)

    async def recv(self) -> bytes:
        return b'{"type":"message","topic":"/spotMarket/tradeOrders","data":{}}'


class _FakeNative:
    KucoinPublicWebSocketClient = _FakeNativeKucoinPublicWebSocketClient
    KucoinPrivateWebSocketClient = _FakeNativeKucoinPrivateWebSocketClient


@pytest.mark.asyncio
async def test_kucoin_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import kucoin

    monkeypatch.setattr(kucoin, "_native", _FakeNative)

    async with kucoin.public(
        timeout=2,
        spot_http_base_url="https://example.test/spot",
        futures_http_base_url="https://example.test/futures",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.timeout == 2
        assert native_client.spot_http_base_url == "https://example.test/spot"
        assert native_client.futures_http_base_url == "https://example.test/futures"

        assert await ws.subscribe_trades("BTC-USDT-SPOT") == "sub-1"
        assert await ws.subscribe_ticker("BTC-USDT-SPOT") == "sub-1"
        assert await ws.subscribe_orderbook("BTC-USDT-SPOT") == "sub-1"
        assert await ws.subscribe_klines("BTC-USDT-SPOT", "1min") == "sub-1"
        assert await ws.ping() == "ping-1"
        event = await ws.recv()

    assert native_client.subscriptions == [
        "/market/match:BTC-USDT-SPOT",
        "/market/ticker:BTC-USDT-SPOT",
        "/market/level2:BTC-USDT-SPOT",
        "/market/candles:BTC-USDT-SPOT_1min",
    ]
    assert native_client.ping_count == 1
    assert event == {
        "type": "message",
        "topic": "/market/match:BTC-USDT",
        "data": {},
    }
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_kucoin_futures_ws_routes_official_topics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import kucoin

    monkeypatch.setattr(kucoin, "_native", _FakeNative)

    async with kucoin.public(market="futures") as public_ws:
        public_native = public_ws._native_client
        assert public_native.market == "futures"
        await public_ws.subscribe_ticker("XBTUSDTM")
        await public_ws.subscribe_trades("XBTUSDTM")
        await public_ws.subscribe_orderbook("XBTUSDTM")
        await public_ws.subscribe_klines("XBTUSDTM", "1min")

    assert public_native.subscriptions == [
        "/contractMarket/tickerV2:XBTUSDTM",
        "/contractMarket/execution:XBTUSDTM",
        "/contractMarket/level2:XBTUSDTM",
        "/contractMarket/limitCandle:XBTUSDTM_1min",
    ]

    async with kucoin.private(
        api_key="api-key",
        api_secret="api-secret",
        passphrase="passphrase",
        market="futures",
    ) as private_ws:
        private_native = private_ws._native_client
        assert private_native.market == "futures"
        await private_ws.subscribe_orders()
        await private_ws.subscribe_balances()

    assert private_native.subscriptions == [
        "/contractMarket/tradeOrders",
        "/contractAccount/wallet",
    ]


@pytest.mark.asyncio
async def test_kucoin_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import kucoin

    class FakeNativeClient(_FakeNativeKucoinPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        KucoinPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(kucoin, "_native", FakeNative)

    ws = kucoin.public()
    with pytest.raises(RuntimeError, match="Unexpected KuCoin WebSocket event payload"):
        await ws.recv()


@pytest.mark.asyncio
async def test_kucoin_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import kucoin

    monkeypatch.setattr(kucoin, "_native", _FakeNative)

    async with kucoin.private(
        api_key="api-key",
        api_secret="api-secret",
        passphrase="passphrase",
        timeout=2,
        spot_http_base_url="https://example.test/spot",
        futures_http_base_url="https://example.test/futures",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.api_key == "api-key"
        assert native_client.api_secret == "api-secret"
        assert native_client.passphrase == "passphrase"
        assert native_client.timeout == 2

        assert await ws.subscribe_orders() == "sub-1"
        assert await ws.subscribe_balances() == "sub-1"
        assert await ws.ping() == "ping-1"
        event = await ws.recv()

    assert native_client.subscriptions == [
        "/spotMarket/tradeOrders",
        "/account/balance",
    ]
    assert native_client.ping_count == 1
    assert event == {
        "type": "message",
        "topic": "/spotMarket/tradeOrders",
        "data": {},
    }
    assert native_client.closed is True
