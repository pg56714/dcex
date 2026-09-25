"""Offline Arcus public-client wiring tests."""

import asyncio
import importlib
from types import SimpleNamespace

import pytest

from dcex.arcus.client import Client as SyncClient
from dcex.async_support.arcus.client import Client as AsyncClient


def test_arcus_perps_uses_one_env_credential_set_for_either_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Network selection changes the endpoint, not the environment key names."""
    native = SimpleNamespace(ArcusHttpClient=lambda **kwargs: kwargs)
    monkeypatch.setattr(importlib.import_module("dcex.arcus.client"), "load_native", lambda: native)
    monkeypatch.setattr(
        importlib.import_module("dcex.async_support.arcus.client"), "load_native", lambda: native
    )
    monkeypatch.setenv("ARCUS_API_KEY", "configured-key")
    monkeypatch.setenv("ARCUS_API_SIGNING_KEY", "configured-seed")
    monkeypatch.setenv("ARCUS_ADDRESS", "0x" + "11" * 20)
    monkeypatch.setenv("ARCUS_ACCOUNT_INDEX", "2")
    monkeypatch.setenv("ARCUS_TESTNET_API_KEY", "legacy-key")
    monkeypatch.setenv("ARCUS_TESTNET_ADDRESS", "0x" + "22" * 20)

    mainnet = SyncClient()
    testnet = SyncClient(testnet=True)
    for client in (mainnet, testnet):
        assert client.api_key == "configured-key"
        assert client.api_secret == "configured-seed"
        assert client.address == "0x" + "11" * 20
        assert client.account_index == 0
        assert client._native_client["testnet"] is client.testnet

    explicit = SyncClient(
        api_key="explicit-key",
        api_secret="explicit-seed",
        address="0x" + "33" * 20,
        account_index=3,
        testnet=True,
    )
    assert explicit.api_key == "explicit-key"
    assert explicit.api_secret == "explicit-seed"
    assert explicit.address == "0x" + "33" * 20
    assert explicit.account_index == 3

    async def check() -> None:
        client = await AsyncClient(testnet=True).async_init()
        assert client.api_key == "configured-key"
        assert client.api_secret == "configured-seed"
        assert client.address == "0x" + "11" * 20
        assert client.account_index == 0
        assert client._native_client["testnet"] is True

    asyncio.run(check())


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

    def private_request_json(
        self, method: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], dict[str, bool]]:
        self.calls.append((method, params))
        return 200, {}, {"ok": True}

    async def private_request_json_async(
        self, method: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], dict[str, bool]]:
        return self.private_request_json(method, params)


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
        assert await client.get_transfer_updates("0x1111111111111111111111111111111111111111") == {
            "ok": True
        }
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


def test_arcus_modify_order_sync_and_async_wrappers() -> None:
    """Both Python variants forward the same modify-order fields to Rust."""
    expected = [
        ("product_symbol", "BTC-USD"),
        ("side", "BUY"),
        ("price", "50000"),
        ("quantity", "0.01"),
        ("good_til_time", "1900000000000000"),
        ("time_in_force", "GTT"),
        ("reduce_only", "false"),
        ("order_id", "abc123"),
    ]
    sync_client = SyncClient()
    sync_native = _Native()
    sync_client._native_client = sync_native
    sync_client.modify_order(
        "BTC-USD",
        "BUY",
        "50000",
        "0.01",
        1900000000000000,
        "GTT",
        False,
        order_id="abc123",
    )
    assert sync_native.calls == [("modify_order", expected)]

    async def check() -> None:
        async_client = await AsyncClient(testnet=True).async_init()
        async_native = _Native()
        async_client._native_client = async_native
        await async_client.modify_order(
            "BTC-USD",
            "BUY",
            "50000",
            "0.01",
            1900000000000000,
            "GTT",
            False,
            order_id="abc123",
        )
        assert async_native.calls == [("modify_order", expected)]

    asyncio.run(check())
