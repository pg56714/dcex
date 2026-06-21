# ruff: noqa: D100, D103

import pytest


class _FakeNativeLighterPublicWebSocketClient:
    def __init__(
        self,
        testnet: bool = False,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self.testnet = testnet
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.pings = 0
        self.subscriptions: list[str] = []
        self.unsubscriptions: list[str] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.pings += 1

    async def subscribe(self, channel: str) -> None:
        self.subscriptions.append(channel)

    async def unsubscribe(self, channel: str) -> None:
        self.unsubscriptions.append(channel)

    async def subscribe_orderbook(self, market_id: int) -> None:
        await self.subscribe(f"order_book/{market_id}")

    async def subscribe_ticker(self, market_id: int) -> None:
        await self.subscribe(f"ticker/{market_id}")

    async def subscribe_market_stats(self, market_id: int) -> None:
        await self.subscribe(f"market_stats/{market_id}")

    async def subscribe_all_market_stats(self) -> None:
        await self.subscribe("market_stats/all")

    async def subscribe_trades(self, market_id: int) -> None:
        await self.subscribe(f"trade/{market_id}")

    async def subscribe_klines(self, market_id: int, resolution: str) -> None:
        await self.subscribe(f"candle/{market_id}/{resolution}")

    async def subscribe_mark_price_klines(self, market_id: int, resolution: str) -> None:
        await self.subscribe(f"mark_price_candle/{market_id}/{resolution}")

    async def subscribe_spot_market_stats(self, market_id: int) -> None:
        await self.subscribe(f"spot_market_stats/{market_id}")

    async def subscribe_all_spot_market_stats(self) -> None:
        await self.subscribe("spot_market_stats/all")

    async def subscribe_height(self) -> None:
        await self.subscribe("height")

    async def recv(self) -> bytes:
        return b'{"channel":"trade:0","type":"update/trade","trades":[]}'


class _FakeNativeLighterPrivateWebSocketClient:
    def __init__(
        self,
        account_index: int,
        api_key_index: int,
        api_private_key: str,
        testnet: bool = False,
        timeout: float = 10.0,
        ws_base_url: str | None = None,
        http_base_url: str | None = None,
    ) -> None:
        self._account_index = account_index
        self.api_key_index = api_key_index
        self.api_private_key = api_private_key
        self.testnet = testnet
        self.timeout = timeout
        self.ws_base_url = ws_base_url
        self.http_base_url = http_base_url
        self.connected = False
        self.closed = False
        self.pings = 0
        self.subscriptions: list[tuple[str, str | None]] = []
        self.unsubscriptions: list[str] = []

    def account_index(self) -> int:
        return self._account_index

    def create_auth_token(
        self,
        deadline: int | None = None,
        api_key_index: int | None = None,
    ) -> str:
        return f"token:{deadline}:{api_key_index}"

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def ping(self) -> None:
        self.pings += 1

    async def subscribe(self, channel: str, auth: str | None = None) -> None:
        self.subscriptions.append((channel, auth))

    async def unsubscribe(self, channel: str) -> None:
        self.unsubscriptions.append(channel)

    async def subscribe_authenticated(self, channel: str) -> None:
        await self.subscribe(channel, "generated")

    async def subscribe_account_all(self) -> None:
        await self.subscribe(f"account_all/{self._account_index}")

    async def subscribe_account_market(self, market_id: int) -> None:
        await self.subscribe_authenticated(f"account_market/{market_id}/{self._account_index}")

    async def subscribe_user_stats(self) -> None:
        await self.subscribe(f"user_stats/{self._account_index}")

    async def subscribe_account_tx(self) -> None:
        await self.subscribe_authenticated(f"account_tx/{self._account_index}")

    async def subscribe_account_all_orders(self) -> None:
        await self.subscribe_authenticated(f"account_all_orders/{self._account_index}")

    async def subscribe_pool_data(self) -> None:
        await self.subscribe_authenticated(f"pool_data/{self._account_index}")

    async def subscribe_pool_info(self) -> None:
        await self.subscribe_authenticated(f"pool_info/{self._account_index}")

    async def subscribe_notifications(self) -> None:
        await self.subscribe_authenticated(f"notification/{self._account_index}")

    async def subscribe_account_orders(self, market_id: int) -> None:
        await self.subscribe_authenticated(f"account_orders/{market_id}/{self._account_index}")

    async def subscribe_account_all_trades(self) -> None:
        await self.subscribe(f"account_all_trades/{self._account_index}")

    async def subscribe_account_all_positions(self) -> None:
        await self.subscribe(f"account_all_positions/{self._account_index}")

    async def subscribe_account_all_assets(self) -> None:
        await self.subscribe_authenticated(f"account_all_assets/{self._account_index}")

    async def subscribe_account_spot_avg_entry_prices(self) -> None:
        await self.subscribe_authenticated(f"account_spot_avg_entry_prices/{self._account_index}")

    async def subscribe_rfq(self) -> None:
        await self.subscribe_authenticated("rfq")

    async def recv(self) -> bytes:
        return b'{"channel":"account_all_orders:42","type":"update/account_all_orders"}'


class _FakeNative:
    LighterPublicWebSocketClient = _FakeNativeLighterPublicWebSocketClient
    LighterPrivateWebSocketClient = _FakeNativeLighterPrivateWebSocketClient


@pytest.mark.asyncio
async def test_lighter_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import lighter

    monkeypatch.setattr(lighter, "_native", _FakeNative)

    async with lighter.public(
        testnet=True,
        timeout=2,
        base_url="wss://example.test/stream",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.testnet is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/stream"

        await ws.ping()
        await ws.subscribe_trades(0)
        await ws.subscribe_orderbook(1)
        await ws.subscribe_klines(2, "1m")
        event = await ws.recv()

    assert native_client.pings == 1
    assert native_client.subscriptions == ["trade/0", "order_book/1", "candle/2/1m"]
    assert event == {"channel": "trade:0", "type": "update/trade", "trades": []}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_lighter_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import lighter

    monkeypatch.setattr(lighter, "_native", _FakeNative)

    async with lighter.private(
        account_index=42,
        api_key_index=7,
        api_private_key="private-key",
        testnet=True,
        timeout=2,
        ws_base_url="wss://example.test/stream",
        http_base_url="https://example.test",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.account_index() == 42
        assert native_client.api_key_index == 7
        assert native_client.api_private_key == "private-key"
        assert native_client.testnet is True
        assert native_client.timeout == 2
        assert native_client.ws_base_url == "wss://example.test/stream"
        assert native_client.http_base_url == "https://example.test"
        assert ws.account_index() == 42
        assert ws.create_auth_token(deadline=60, api_key_index=7) == "token:60:7"

        await ws.ping()
        await ws.subscribe_account_all()
        await ws.subscribe_account_all_orders()
        await ws.subscribe_account_orders(0)
        event = await ws.recv()

    assert native_client.pings == 1
    assert native_client.subscriptions == [
        ("account_all/42", None),
        ("account_all_orders/42", "generated"),
        ("account_orders/0/42", "generated"),
    ]
    assert event == {"channel": "account_all_orders:42", "type": "update/account_all_orders"}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_lighter_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import lighter

    class FakeNativeClient(_FakeNativeLighterPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        LighterPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(lighter, "_native", FakeNative)

    ws = lighter.public()
    with pytest.raises(RuntimeError, match="Unexpected Lighter WebSocket event payload"):
        await ws.recv()
