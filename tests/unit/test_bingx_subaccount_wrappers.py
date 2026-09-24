"""Regression coverage for BingX sub-account wrappers."""

# ruff: noqa: ANN001, ANN202, D103

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    def private_request_json(self, method_name, params):
        self.calls.append((method_name, params))
        return 200, {}, {"code": 0, "data": {}}


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    async def private_request_json_async(self, method_name, params):
        self.calls.append((method_name, params))
        return 200, {}, {"code": 0, "data": {}}


def test_sync_bingx_subaccount_wrappers_forward_official_fields() -> None:
    from dcex.bingx.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_subaccounts(1, 100, subUid=22, isFeeze=False)
    client.get_subaccount_assets(22)
    client.get_subaccount_all_account_balance(1, 10, subUid=22, accountType="spot")
    client.get_subaccount_transfer_history(22, type_="FUND_SUB", pagingSize=20)
    client.get_subaccount_transferable_amounts(11, 1, 22, 3)
    client.transfer_subaccount_assets("USDT", "1", 11, 1, 1, 22, 2, 3, "funding")

    assert native.calls[0] == (
        "get_subaccounts",
        [
            ("page", "1"),
            ("limit", "100"),
            ("subUid", "22"),
            ("isFeeze", "false"),
        ],
    )
    assert native.calls[1] == ("get_subaccount_assets", [("subUid", "22")])
    assert native.calls[3] == (
        "get_subaccount_transfer_history",
        [("uid", "22"), ("type", "FUND_SUB"), ("pagingSize", "20")],
    )
    assert native.calls[4] == (
        "get_subaccount_transferable_amounts",
        [
            ("fromUid", "11"),
            ("fromAccountType", "1"),
            ("toUid", "22"),
            ("toAccountType", "3"),
        ],
    )
    assert native.calls[5][0] == "transfer_subaccount_assets"
    assert native.calls[5][1][-1] == ("remark", "funding")


@pytest.mark.asyncio
async def test_async_bingx_subaccount_wrappers_forward_official_fields() -> None:
    from dcex.async_support.bingx.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_subaccounts(subAccountString="alpha1", limit=10)
    await client.get_subaccount_assets("22", recvWindow=5_000)
    await client.get_subaccount_all_account_balance(accountType="stdFutures")
    await client.get_subaccount_transfer_history("22", pageId=1, pagingSize=100)

    assert native.calls == [
        (
            "get_subaccounts",
            [("page", "1"), ("limit", "10"), ("subAccountString", "alpha1")],
        ),
        (
            "get_subaccount_assets",
            [("subUid", "22"), ("recvWindow", "5000")],
        ),
        (
            "get_subaccount_all_account_balance",
            [("pageIndex", "1"), ("pageSize", "10"), ("accountType", "stdFutures")],
        ),
        (
            "get_subaccount_transfer_history",
            [("uid", "22"), ("pageId", "1"), ("pagingSize", "100")],
        ),
    ]
