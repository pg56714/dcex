# ruff: noqa: D100, D103

import json

import pytest


class _FakeNativeHyperliquidPublicWebSocketClient:
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
        self.subscriptions: list[dict[str, object]] = []
        self.unsubscriptions: list[dict[str, object]] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def subscribe(self, subscription_json: bytes) -> None:
        self.subscriptions.append(json.loads(subscription_json))

    async def unsubscribe(self, subscription_json: bytes) -> None:
        self.unsubscriptions.append(json.loads(subscription_json))

    async def subscribe_all_mids(self, dex: str | None = None) -> None:
        subscription: dict[str, object] = {"type": "allMids"}
        if dex is not None:
            subscription["dex"] = dex
        self.subscriptions.append(subscription)

    async def subscribe_trades(self, product_symbol: str) -> None:
        self.subscriptions.append({"type": "trades", "coin": product_symbol})

    async def subscribe_orderbook(self, product_symbol: str) -> None:
        self.subscriptions.append({"type": "l2Book", "coin": product_symbol})

    async def subscribe_l2_book(
        self,
        product_symbol: str,
        n_sig_figs: int | None = None,
        mantissa: int | None = None,
    ) -> None:
        subscription: dict[str, object] = {"type": "l2Book", "coin": product_symbol}
        if n_sig_figs is not None:
            subscription["nSigFigs"] = n_sig_figs
        if mantissa is not None:
            subscription["mantissa"] = mantissa
        self.subscriptions.append(subscription)

    async def subscribe_bbo(self, product_symbol: str) -> None:
        self.subscriptions.append({"type": "bbo", "coin": product_symbol})

    async def subscribe_klines(self, product_symbol: str, interval: str) -> None:
        self.subscriptions.append({"type": "candle", "coin": product_symbol, "interval": interval})

    async def subscribe_active_asset_ctx(self, product_symbol: str) -> None:
        self.subscriptions.append({"type": "activeAssetCtx", "coin": product_symbol})

    async def recv(self) -> bytes:
        return b'{"channel":"trades","data":[{"coin":"BTC"}]}'


class _FakeNativeHyperliquidPrivateWebSocketClient:
    def __init__(
        self,
        user: str,
        testnet: bool = False,
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        self._user = user
        self.testnet = testnet
        self.timeout = timeout
        self.base_url = base_url
        self.connected = False
        self.closed = False
        self.subscriptions: list[dict[str, object]] = []
        self.unsubscriptions: list[dict[str, object]] = []

    def user(self) -> str:
        return self._user

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def subscribe(self, subscription_json: bytes) -> None:
        self.subscriptions.append(json.loads(subscription_json))

    async def unsubscribe(self, subscription_json: bytes) -> None:
        self.unsubscriptions.append(json.loads(subscription_json))

    async def subscribe_user_subscription(
        self,
        subscription_type: str,
        dex: str | None = None,
    ) -> None:
        subscription: dict[str, object] = {"type": subscription_type, "user": self._user}
        if dex is not None:
            subscription["dex"] = dex
        self.subscriptions.append(subscription)

    async def unsubscribe_user_subscription(
        self,
        subscription_type: str,
        dex: str | None = None,
    ) -> None:
        subscription: dict[str, object] = {"type": subscription_type, "user": self._user}
        if dex is not None:
            subscription["dex"] = dex
        self.unsubscriptions.append(subscription)

    async def subscribe_notifications(self) -> None:
        await self.subscribe_user_subscription("notification")

    async def subscribe_web_data3(self) -> None:
        await self.subscribe_user_subscription("webData3")

    async def subscribe_clearinghouse_state(self, dex: str | None = None) -> None:
        await self.subscribe_user_subscription("clearinghouseState", dex)

    async def subscribe_open_orders(self, dex: str | None = None) -> None:
        await self.subscribe_user_subscription("openOrders", dex)

    async def subscribe_order_updates(self) -> None:
        await self.subscribe_user_subscription("orderUpdates")

    async def subscribe_user_events(self) -> None:
        await self.subscribe_user_subscription("userEvents")

    async def subscribe_user_fills(
        self,
        aggregate_by_time: bool | None = None,
    ) -> None:
        subscription: dict[str, object] = {"type": "userFills", "user": self._user}
        if aggregate_by_time is not None:
            subscription["aggregateByTime"] = aggregate_by_time
        self.subscriptions.append(subscription)

    async def subscribe_user_fundings(self) -> None:
        await self.subscribe_user_subscription("userFundings")

    async def subscribe_user_non_funding_ledger_updates(self) -> None:
        await self.subscribe_user_subscription("userNonFundingLedgerUpdates")

    async def subscribe_twap_states(self, dex: str | None = None) -> None:
        await self.subscribe_user_subscription("twapStates", dex)

    async def subscribe_user_twap_slice_fills(self) -> None:
        await self.subscribe_user_subscription("userTwapSliceFills")

    async def subscribe_user_twap_history(self) -> None:
        await self.subscribe_user_subscription("userTwapHistory")

    async def subscribe_active_asset_data(self, product_symbol: str) -> None:
        self.subscriptions.append(
            {
                "type": "activeAssetData",
                "user": self._user,
                "coin": product_symbol,
            }
        )

    async def recv(self) -> bytes:
        return b'{"channel":"userEvents","data":{"fills":[]}}'


class _FakeNative:
    HyperliquidPublicWebSocketClient = _FakeNativeHyperliquidPublicWebSocketClient
    HyperliquidPrivateWebSocketClient = _FakeNativeHyperliquidPrivateWebSocketClient


@pytest.mark.asyncio
async def test_hyperliquid_public_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import hyperliquid

    monkeypatch.setattr(hyperliquid, "_native", _FakeNative)

    async with hyperliquid.public(
        testnet=True,
        timeout=2,
        base_url="wss://example.test/ws",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.testnet is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"

        await ws.subscribe({"type": "trades", "coin": "BTC"})
        await ws.subscribe_all_mids(dex="main")
        await ws.subscribe_l2_book("BTC", n_sig_figs=5, mantissa=1)
        await ws.subscribe_klines("ETH", "1m")
        event = await ws.recv()

    assert native_client.subscriptions == [
        {"type": "trades", "coin": "BTC"},
        {"type": "allMids", "dex": "main"},
        {"type": "l2Book", "coin": "BTC", "nSigFigs": 5, "mantissa": 1},
        {"type": "candle", "coin": "ETH", "interval": "1m"},
    ]
    assert event == {"channel": "trades", "data": [{"coin": "BTC"}]}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_hyperliquid_private_ws_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import hyperliquid

    monkeypatch.setattr(hyperliquid, "_native", _FakeNative)
    user = "0x0000000000000000000000000000000000000001"

    async with hyperliquid.private(
        user=user,
        testnet=True,
        timeout=2,
        base_url="wss://example.test/ws",
    ) as ws:
        native_client = ws._native_client
        assert native_client.connected is True
        assert native_client.testnet is True
        assert native_client.timeout == 2
        assert native_client.base_url == "wss://example.test/ws"
        assert ws.user() == user

        await ws.subscribe_open_orders(dex="main")
        await ws.subscribe_order_updates()
        await ws.subscribe_user_fills(aggregate_by_time=True)
        await ws.subscribe_active_asset_data("BTC")
        event = await ws.recv()

    assert native_client.subscriptions == [
        {"type": "openOrders", "user": user, "dex": "main"},
        {"type": "orderUpdates", "user": user},
        {"type": "userFills", "user": user, "aggregateByTime": True},
        {"type": "activeAssetData", "user": user, "coin": "BTC"},
    ]
    assert event == {"channel": "userEvents", "data": {"fills": []}}
    assert native_client.closed is True


@pytest.mark.asyncio
async def test_hyperliquid_ws_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("dcex._native")
    from dcex.ws import hyperliquid

    class FakeNativeClient(_FakeNativeHyperliquidPublicWebSocketClient):
        async def recv(self) -> bytes:
            return b'"unexpected"'

    class FakeNative:
        HyperliquidPublicWebSocketClient = FakeNativeClient

    monkeypatch.setattr(hyperliquid, "_native", FakeNative)

    ws = hyperliquid.public()
    with pytest.raises(RuntimeError, match="Unexpected Hyperliquid WebSocket event payload"):
        await ws.recv()
