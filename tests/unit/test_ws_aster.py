# ruff: noqa: D100, D103

import pytest


class _FakeNativeAsterPublicWebSocketClient:
    def __init__(
        self,
        market: str = "futures",
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.market = market
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

    async def list_subscriptions(self) -> int:
        return 3

    async def subscribe_trades(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:trade")
        return 4

    async def subscribe_agg_trades(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:aggTrade")
        return 5

    async def subscribe_orderbook(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:depth")
        return 6

    async def subscribe_book_ticker(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:bookTicker")
        return 7

    async def subscribe_ticker(self, product_symbol: str) -> int:
        self.streams.append(f"{product_symbol}:ticker")
        return 8

    async def subscribe_klines(self, product_symbol: str, interval: str) -> int:
        self.streams.append(f"{product_symbol}:kline_{interval}")
        return 9

    async def subscribe_mark_price(self, product_symbol: str, fast: bool = False) -> int:
        speed = "@1s" if fast else ""
        self.streams.append(f"{product_symbol}:markPrice{speed}")
        return 10

    async def recv(self) -> bytes:
        return b'{"e":"trade","s":"BTCUSDT"}'


class _FakeNativeAsterPrivateWebSocketClient:
    def __init__(
        self,
        signer_address: str,
        private_key: str,
        user_address: str | None = None,
        market: str = "futures",
        timeout: float = 10.0,
        spot_http_base_url: str | None = None,
        futures_http_base_url: str | None = None,
        ws_base_url: str | None = None,
    ) -> None:
        self.signer_address = signer_address
        self.private_key = private_key
        self.user_address = user_address
        self.market = market
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

    async def connect_with_listen_key(self, listen_key: str) -> None:
        self.connected = True
        self._listen_key = listen_key

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


class _FakeNative:
    AsterPublicWebSocketClient = _FakeNativeAsterPublicWebSocketClient
    AsterPrivateWebSocketClient = _FakeNativeAsterPrivateWebSocketClient


@pytest.mark.asyncio
async def test_aster_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import aster

    monkeypatch.setattr(aster, "_native", _FakeNative)

    async with aster.public(
        market="spot",
        timeout=2,
        base_url="wss://example.test/ws",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.market == "spot"
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        assert await ws.subscribe_trades("BTC-USDT-SPOT") == 4
        assert await ws.subscribe_book_ticker("BTC-USDT-SPOT") == 7
        assert await ws.subscribe_mark_price("BTC-USDT-SWAP", fast=True) == 10
        event = await ws.recv()

    assert event == {"e": "trade", "s": "BTCUSDT"}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_aster_public_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import aster

    class FakeNativeClient(_FakeNativeAsterPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        AsterPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(aster, "_native", FakeNative)

    ws = aster.public()
    with pytest.raises(RuntimeError, match="Unexpected Aster WebSocket event payload"):
        await ws.recv()


@pytest.mark.asyncio
async def test_aster_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import aster

    monkeypatch.setattr(aster, "_native", _FakeNative)

    async with aster.private(
        user_address="0xuser",
        signer_address="0xsigner",
        private_key="0xkey",
        market="futures",
        timeout=2,
        futures_http_base_url="https://example.test/fapi",
        ws_base_url="wss://example.test",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.user_address == "0xuser"
        assert native_client.signer_address == "0xsigner"
        assert native_client.private_key == "0xkey"
        assert native_client.market == "futures"
        assert native_client.timeout == 2
        assert native_client.futures_http_base_url == "https://example.test/fapi"
        assert native_client.ws_base_url == "wss://example.test"
        assert ws.listen_key() == "listen-key"

        await ws.keep_alive()
        event = await ws.recv()

    assert event == {"e": "ACCOUNT_UPDATE", "E": 123}
    assert native_client.keep_alive_count == 1
    assert native_client.closed is True
    assert ws.listen_key() is None


@pytest.mark.asyncio
async def test_aster_private_ws_connect_with_listen_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import aster

    monkeypatch.setattr(aster, "_native", _FakeNative)

    ws = aster.private(
        signer_address="0xsigner",
        private_key="0xkey",
        market="spot",
    )
    await ws.connect_with_listen_key("existing")

    assert ws.listen_key() == "existing"
