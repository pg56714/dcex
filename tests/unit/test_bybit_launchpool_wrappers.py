"""Regression coverage for Bybit Launchpool sync and async wrappers."""

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[tuple[str, str]]]] = []

    def public_request_json(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(("public", method_name, params))
        return 200, {}, {"retCode": 0, "result": {}}

    def private_request_json(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(("private", method_name, params))
        return 200, {}, {"retCode": 0, "result": {}}


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[tuple[str, str]]]] = []

    async def public_request_json_async(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(("public", method_name, params))
        return 200, {}, {"retCode": 0, "result": {}}

    async def private_request_json_async(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(("private", method_name, params))
        return 200, {}, {"retCode": 0, "result": {}}


def test_launchpool_sync_wrappers_forward_official_fields() -> None:
    """Sync wrappers forward public and signed read-only filters."""
    from dcex.bybit.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_launchpool_projects(1, activityCoin="BTC", limit=10)
    client.get_launchpool_current_staking()
    client.get_launchpool_activity_log(stakeCoin="USDT", type=0, pageSize=10)
    client.get_launchpool_history(rewardCoin="BTC", current=2)

    assert native.calls[0] == (
        "public",
        "get_launchpool_projects",
        [("status", "1"), ("activityCoin", "BTC"), ("limit", "10")],
    )
    assert native.calls[1] == ("private", "get_launchpool_current_staking", [])
    assert ("type", "0") in native.calls[2][2]
    assert ("current", "2") in native.calls[3][2]


@pytest.mark.asyncio
async def test_launchpool_async_wrappers_forward_official_fields() -> None:
    """Async wrappers forward public and signed read-only filters."""
    from dcex.async_support.bybit.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_launchpool_projects(2, projectId="project-1")
    await client.get_launchpool_activity_log(status=1, current=3)
    await client.get_launchpool_history(stakeCoin="USDT", pageSize=5)

    assert native.calls[0] == (
        "public",
        "get_launchpool_projects",
        [("status", "2"), ("projectId", "project-1")],
    )
    assert ("status", "1") in native.calls[1][2]
    assert ("pageSize", "5") in native.calls[2][2]
