"""Offline Ondo Python request-wire checks."""

import asyncio

import pytest

from dcex.async_support.ondo.client import Client as AsyncClient
from dcex.ondo.client import Client as SyncClient


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[tuple[str, str]]]] = []

    def public_request_json(
        self,
        method: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], dict[str, bool]]:
        self.calls.append(("public", method, params))
        return 200, {}, {"success": True}

    def private_request_json(
        self,
        method: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], dict[str, bool]]:
        self.calls.append(("private", method, params))
        return 200, {}, {"success": True}


class _AsyncNative(_SyncNative):
    async def public_request_json_async(
        self,
        method: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], dict[str, bool]]:
        return super().public_request_json(method, params)

    async def private_request_json_async(
        self,
        method: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], dict[str, bool]]:
        return super().private_request_json(method, params)


def test_sync_ondo_public_and_private_fields_are_encoded() -> None:
    """Sync wrappers serialize Ondo body and query fields exactly."""
    client = SyncClient(preload_product_table=False)
    native = _SyncNative()
    client._native_client = native
    assert client.get_contracts(sparkline=True) == {"success": True}
    assert client.get_price_history("AAPLUSD.P", "1H", 100, 200) == {"success": True}
    assert client.place_order(
        market="AAPL-USD.P",
        side="buy",
        type="limit",
        price="100",
        size="1",
        reduceOnly=False,
    ) == {"success": True}
    assert native.calls == [
        ("public", "get_contracts", [("sparkline", "true")]),
        (
            "public",
            "get_price_history",
            [
                ("symbol", "AAPLUSD.P"),
                ("resolution", "1H"),
                ("from", "100"),
                ("to", "200"),
            ],
        ),
        (
            "private",
            "place_order",
            [
                ("market", "AAPL-USD.P"),
                ("side", "buy"),
                ("type", "limit"),
                ("price", "100"),
                ("size", "1"),
                ("reduceOnly", "false"),
            ],
        ),
    ]


def test_async_ondo_methods_match_sync_wire_fields() -> None:
    """Async wrappers use the same documented field names."""

    async def check() -> None:
        client = await AsyncClient(preload_product_table=False).async_init()
        native = _AsyncNative()
        client._native_client = native
        assert await client.get_klines("AAPL-USD.P", "1H", 100, 200) == {"success": True}
        assert await client.get_depth("AAPL-USD.P", 10) == {"success": True}
        assert native.calls == [
            (
                "private",
                "get_klines",
                [
                    ("market", "AAPL-USD.P"),
                    ("resolution", "1H"),
                    ("from", "100"),
                    ("to", "200"),
                ],
            ),
            ("public", "get_depth", [("market", "AAPL-USD.P"), ("depth", "10")]),
        ]

    asyncio.run(check())


def test_ondo_requires_complete_api_key_pair(monkeypatch: pytest.MonkeyPatch) -> None:
    """A partial API-key pair is rejected before any transport call."""
    monkeypatch.delenv("ONDO_API_KEY_ID", raising=False)
    monkeypatch.delenv("ONDO_API_SECRET", raising=False)
    try:
        SyncClient(api_key_id="key", api_secret=None, preload_product_table=False)
    except ValueError:
        return
    except RuntimeError as exc:
        assert "api_key_id and api_secret" in str(exc)
        return
    raise AssertionError("partial Ondo API credentials must be rejected")


def test_ondo_batch_cancel_uses_comma_separated_order_ids() -> None:
    """Batch cancellation uses the documented single query string field."""
    client = SyncClient(preload_product_table=False)
    native = _SyncNative()
    client._native_client = native
    client.batch_cancel_orders(["abc123", "def456"])
    assert native.calls == [("private", "batch_cancel_orders", [("orderIDs", "abc123,def456")])]
    with pytest.raises(ValueError):
        client.batch_cancel_orders(["abc123", ""])


def test_ondo_account_management_fields_are_encoded() -> None:
    """State-changing account wrappers preserve the official request fields."""
    client = SyncClient(preload_product_table=False)
    native = _SyncNative()
    client._native_client = native

    assert not hasattr(client, "withdraw")
    assert not hasattr(client, "sandbox_withdrawal")
    client.create_api_key("trader", ["trade", "transfer"])
    client.get_withdrawal_status(customer_withdrawal_id="withdrawal-id")
    client.set_api_key_ip_whitelist("api-key-id", "192.0.2.1")

    assert native.calls == [
        (
            "private",
            "create_api_key",
            [("name", "trader"), ("scopes", '["trade","transfer"]')],
        ),
        (
            "private",
            "get_withdrawal_status",
            [("customer_withdrawal_id", "withdrawal-id")],
        ),
        (
            "private",
            "set_api_key_ip_whitelist",
            [("apiKeyID", "api-key-id"), ("ip", "192.0.2.1")],
        ),
    ]
