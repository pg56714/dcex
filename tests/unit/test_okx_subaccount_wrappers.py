"""Regression coverage for OKX sub-account wrappers."""
# ruff: noqa: ANN001, ANN202, D103

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    def private_request_json(self, method_name, params):
        self.calls.append((method_name, params))
        return 200, {}, {"code": "0", "data": []}


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    async def private_request_json_async(self, method_name, params):
        self.calls.append((method_name, params))
        return 200, {}, {"code": "0", "data": []}


def test_sync_okx_subaccount_wrappers_forward_official_fields() -> None:
    from dcex.okx.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_subaccount_list(enable=True, limit=20)
    client.get_subaccount_trading_balance("alpha")
    client.get_subaccount_funding_balance("alpha", ["BTC", "USDT"])
    client.get_subaccount_bills("alpha", ccy="USDT", limit=10)
    client.transfer_between_subaccounts(
        "USDT",
        "1",
        "FUND",
        "TRADING",
        "alpha",
        "beta",
        loanTrans=False,
    )
    client.get_entrusted_subaccount_list("alpha")
    client.get_subaccount_interest_limits("alpha", ccy="USDT")

    assert native.calls[0] == (
        "get_subaccount_list",
        [("enable", "true"), ("limit", "20")],
    )
    assert native.calls[2][1] == [
        ("subAcct", "alpha"),
        ("ccy", '["BTC","USDT"]'),
    ]
    assert native.calls[4][1][-1] == ("loanTrans", "false")
    assert native.calls[-1][1] == [("subAcct", "alpha"), ("ccy", "USDT")]


@pytest.mark.asyncio
async def test_async_okx_subaccount_wrappers_forward_official_fields() -> None:
    from dcex.async_support.okx.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_subaccount_list(subAcct="alpha")
    await client.get_subaccount_trading_balance("alpha")
    await client.get_subaccount_funding_balance("alpha", ["USDT"])
    await client.get_subaccount_bills("alpha", type="1")
    await client.get_entrusted_subaccount_list()
    await client.get_subaccount_interest_limits("alpha", ccy="USDT")

    assert native.calls[0] == ("get_subaccount_list", [("subAcct", "alpha")])
    assert native.calls[2][1] == [("subAcct", "alpha"), ("ccy", '["USDT"]')]
    assert native.calls[-1] == (
        "get_subaccount_interest_limits",
        [("subAcct", "alpha"), ("ccy", "USDT")],
    )
