"""Regression coverage for OKX OKUSD wrappers."""
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


def test_sync_okx_okusd_wrappers_forward_official_fields() -> None:
    from dcex.okx.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_okusd_limits()
    client.get_okusd_account()
    client.get_okusd_rate_history(limit=20, begin="1", end="2")
    client.get_okusd_subscribe_history(limit=20)
    client.get_okusd_redeem_history(type="1")
    client.get_okusd_rewards_history(limit=20)
    client.subscribe_okusd("1", "subscribe-1")
    client.redeem_okusd("1", "2", "redeem-1")

    assert native.calls[2] == (
        "get_okusd_rate_history",
        [("limit", "20"), ("begin", "1"), ("end", "2")],
    )
    assert native.calls[6] == (
        "subscribe_okusd",
        [("amt", "1"), ("clOrdId", "subscribe-1")],
    )
    assert native.calls[7] == (
        "redeem_okusd",
        [("amt", "1"), ("redeemType", "2"), ("clOrdId", "redeem-1")],
    )


@pytest.mark.asyncio
async def test_async_okx_okusd_wrappers_forward_official_fields() -> None:
    from dcex.async_support.okx.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_okusd_limits()
    await client.get_okusd_account()
    await client.get_okusd_redeem_history(limit=10, type="2")
    await client.get_okusd_rewards_history(begin="1", end="2")

    assert native.calls[2] == (
        "get_okusd_redeem_history",
        [("limit", "10"), ("type", "2")],
    )
    assert native.calls[-1][1] == [("begin", "1"), ("end", "2")]
