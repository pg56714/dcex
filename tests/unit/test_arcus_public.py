"""Offline Arcus public-client wiring tests."""

import asyncio

from dcex.arcus.client import Client as SyncClient
from dcex.async_support.arcus.client import Client as AsyncClient


class _Native:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    def public_request_json(
        self, method: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], dict[str, bool]]:
        self.calls.append((method, params))
        return 200, {}, {"ok": True}

    async def public_request_json_async(
        self, method: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], dict[str, bool]]:
        return self.public_request_json(method, params)


def test_arcus_sync_public_market_parameters() -> None:
    """Public wrappers send official display names and nLevels."""
    client = SyncClient()
    native = _Native()
    client._native_client = native
    assert client.get_markets() == {"ok": True}
    assert client.get_spot_assets() == {"ok": True}
    assert client.get_fee_tiers() == {"ok": True}
    assert client.get_bbo("BTC-USD") == {"ok": True}
    assert client.get_l2_orderbook("BTC-USD", 5) == {"ok": True}
    assert native.calls == [
        ("get_markets", []),
        ("get_spot_assets", []),
        ("get_fee_tiers", []),
        ("get_bbo", [("market", "BTC-USD")]),
        ("get_l2_orderbook", [("market", "BTC-USD"), ("nLevels", "5")]),
    ]


def test_arcus_async_public_market_parameters() -> None:
    """Async wrappers use the same public request fields."""

    async def check() -> None:
        client = await AsyncClient(testnet=True).async_init()
        native = _Native()
        client._native_client = native
        assert await client.get_bbo("ETH-USD") == {"ok": True}
        assert await client.get_transfer_updates(
            "0x1111111111111111111111111111111111111111"
        ) == {"ok": True}
        assert native.calls == [
            ("get_bbo", [("market", "ETH-USD")]),
            (
                "get_transfer_updates",
                [
                    ("address", "0x1111111111111111111111111111111111111111"),
                    ("accountIndex", "0"),
                ],
            ),
        ]

    asyncio.run(check())
