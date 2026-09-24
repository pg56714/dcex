"""Regression coverage for MEXC sub-account wrappers."""

# ruff: noqa: ANN001, ANN202, D103

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    def private_request_json(self, method_name, params):
        self.calls.append((method_name, params))
        return 200, {}, {"subAccounts": []}


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    async def private_request_json_async(self, method_name, params):
        self.calls.append((method_name, params))
        return 200, {}, {"subAccounts": []}


def test_sync_mexc_subaccount_wrappers_forward_official_fields() -> None:
    from dcex.mexc.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_subaccounts(subAccount="alpha", isFreeze=False, page=1, limit=20)
    client.get_subaccount_asset("alpha")
    client.transfer_subaccount_assets(
        "SPOT",
        "FUTURES",
        "USDT",
        "1",
        fromAccount="alpha",
    )
    client.get_subaccount_transfer_history(
        "FUTURES",
        "SPOT",
        toAccount="alpha",
        page=1,
        limit=100,
    )

    assert native.calls == [
        (
            "get_subaccounts",
            [
                ("subAccount", "alpha"),
                ("isFreeze", "false"),
                ("page", "1"),
                ("limit", "20"),
            ],
        ),
        (
            "get_subaccount_asset",
            [("subAccount", "alpha"), ("accountType", "SPOT")],
        ),
        (
            "transfer_subaccount_assets",
            [
                ("fromAccount", "alpha"),
                ("fromAccountType", "SPOT"),
                ("toAccountType", "FUTURES"),
                ("asset", "USDT"),
                ("amount", "1"),
            ],
        ),
        (
            "get_subaccount_transfer_history",
            [
                ("toAccount", "alpha"),
                ("fromAccountType", "FUTURES"),
                ("toAccountType", "SPOT"),
                ("page", "1"),
                ("limit", "100"),
            ],
        ),
    ]


@pytest.mark.asyncio
async def test_async_mexc_subaccount_wrappers_forward_official_fields() -> None:
    from dcex.async_support.mexc.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_subaccounts(limit=200)
    await client.get_subaccount_asset("beta", recvWindow=5_000)
    await client.get_subaccount_transfer_history(
        "SPOT",
        "SPOT",
        fromAccount="alpha",
        toAccount="beta",
        limit=500,
    )

    assert native.calls == [
        ("get_subaccounts", [("limit", "200")]),
        (
            "get_subaccount_asset",
            [
                ("subAccount", "beta"),
                ("accountType", "SPOT"),
                ("recvWindow", "5000"),
            ],
        ),
        (
            "get_subaccount_transfer_history",
            [
                ("fromAccount", "alpha"),
                ("toAccount", "beta"),
                ("fromAccountType", "SPOT"),
                ("toAccountType", "SPOT"),
                ("limit", "500"),
            ],
        ),
    ]
