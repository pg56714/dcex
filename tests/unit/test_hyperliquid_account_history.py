"""Offline wrapper tests for Hyperliquid time-ranged account history."""

import asyncio
import json
from unittest.mock import AsyncMock, Mock

import pytest

from dcex.async_support.hyperliquid._account_http import AccountHTTP as AsyncAccountHTTP
from dcex.hyperliquid._account_http import AccountHTTP
from tests.unit.native_http_helpers import _http_server

USER = "0x" + "11" * 20


def test_sync_history_wrappers_forward_timestamp_fields() -> None:
    """Synchronous methods send the documented milliseconds fields to Rust."""
    client = object.__new__(AccountHTTP)
    client._native_public = Mock(return_value={"ok": True})
    client.user_fills_by_time(USER, 1000, 2000, True)
    client.user_funding(USER, 1000, 2000)
    client.user_non_funding_ledger_updates(USER, 1000)
    calls = client._native_public.call_args_list
    assert calls[0].args == (
        "user_fills_by_time",
        [("user", USER), ("startTime", "1000"), ("endTime", "2000"), ("aggregateByTime", "true")],
    )
    assert calls[1].args == (
        "user_funding",
        [("user", USER), ("startTime", "1000"), ("endTime", "2000")],
    )
    assert calls[2].args == (
        "user_non_funding_ledger_updates",
        [("user", USER), ("startTime", "1000")],
    )


def test_async_history_wrappers_forward_timestamp_fields() -> None:
    """Asynchronous methods preserve the same native request names."""

    async def check() -> None:
        client = object.__new__(AsyncAccountHTTP)
        client._native_public = AsyncMock(return_value={"ok": True})
        await client.user_fills_by_time(USER, 1000)
        await client.user_funding(USER, 1000)
        await client.user_non_funding_ledger_updates(USER, 1000)
        assert [call.args[0] for call in client._native_public.call_args_list] == [
            "user_fills_by_time",
            "user_funding",
            "user_non_funding_ledger_updates",
        ]

    asyncio.run(check())


def test_native_time_range_payload_reaches_http() -> None:
    """PyO3 and Rust produce the documented Hyperliquid info payload."""
    native = pytest.importorskip("dcex._native")
    with _http_server({"ok": True}) as (base_url, received):
        client = native.HyperliquidHttpClient(timeout=2, endpoint=base_url)
        client.public_request_json(
            "user_fills_by_time",
            [
                ("user", USER),
                ("startTime", "1000"),
                ("endTime", "2000"),
                ("aggregateByTime", "true"),
            ],
        )
        client.public_request_json(
            "user_funding",
            [("user", USER), ("startTime", "1000")],
        )
        client.public_request_json(
            "user_non_funding_ledger_updates",
            [("user", USER), ("startTime", "1000")],
        )
    payloads = [json.loads(received.get_nowait()["body"]) for _ in range(3)]
    assert [payload["type"] for payload in payloads] == [
        "userFillsByTime",
        "userFunding",
        "userNonFundingLedgerUpdates",
    ]
    assert payloads[0]["endTime"] == 2000
    assert payloads[0]["aggregateByTime"] is True
