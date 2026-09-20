"""Offline Arcus WebSocket channel wiring tests."""

import asyncio
from types import SimpleNamespace

import pytest

from dcex.ws import arcus


class _Native:
    def __init__(self, *, testnet: bool, timeout: float) -> None:
        self.testnet = testnet
        self.timeout = timeout
        self.subscriptions: list[tuple[str, str | None]] = []

    async def subscribe(self, channel: str, id: str | None) -> None:
        self.subscriptions.append((channel, id))

    async def recv(self) -> bytes:
        return b'{"type":"subscribed","channel":"markets","contents":[]}'


def test_arcus_market_and_account_subscriptions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Market and address-scoped channels carry the official subscription IDs."""
    monkeypatch.setattr(
        arcus, "load_native", lambda: SimpleNamespace(ArcusWebSocketClient=_Native)
    )

    async def check() -> None:
        public = arcus.PublicClient(testnet=True)
        await public.subscribe_bbo("BTC-USD")
        await public.subscribe("markets")
        assert await public.recv() == {
            "type": "subscribed",
            "channel": "markets",
            "contents": [],
        }
        assert public._native_client.subscriptions == [
            ("bbo", "BTC-USD"),
            ("markets", None),
        ]
        account = arcus.PrivateClient("0x1234")
        await account.subscribe_orders()
        await account.subscribe_fills()
        assert account._native_client.subscriptions == [
            ("orders", "0x1234"),
            ("userFills", "0x1234"),
        ]

    asyncio.run(check())
