"""Regression coverage for Bybit RFQ sync and async wrappers."""

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


def test_sync_bybit_rfq_wrappers_forward_official_fields() -> None:
    """Sync wrappers preserve RFQ JSON, identifiers, and filters."""
    from dcex.bybit.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_rfq_public_trades(limit=20)
    client.get_rfq_config()
    client.create_rfq(
        ["desk"],
        [{"category": "option", "symbol": "BTC-C", "side": "Buy", "qty": "1"}],
        anonymous=True,
    )
    client.create_rfq_quote(
        "rfq-1",
        quoteBuyList=[{"category": "option", "symbol": "BTC-C", "price": "1"}],
        expireIn=60,
    )
    client.execute_rfq_quote("rfq-1", "quote-1", "Buy", isHedge=True)
    client.get_rfq_details(traderType="request", status="Filled", limit=50)

    assert native.calls[0] == (
        "private",
        "get_rfq_public_trades",
        [("limit", "20")],
    )
    assert native.calls[1] == ("private", "get_rfq_config", [])
    assert ("counterparties", '["desk"]') in native.calls[2][2]
    assert ("anonymous", "true") in native.calls[2][2]
    assert ("expireIn", "60") in native.calls[3][2]
    assert native.calls[4][2][-1] == ("isHedge", "true")
    assert native.calls[5][1] == "get_rfq_details"


@pytest.mark.asyncio
async def test_async_bybit_rfq_wrappers_forward_official_fields() -> None:
    """Async wrappers preserve cancellation and history parameters."""
    from dcex.async_support.bybit.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.cancel_rfq(rfqLinkId="client1")
    await client.cancel_rfq_quote(quoteId="quote-1")
    await client.accept_other_rfq_quote("rfq-1")
    await client.get_realtime_rfq_quotes(rfqId="rfq-1", traderType="request")
    await client.get_rfq_trade_history(status="Failed", cursor="next")

    assert native.calls[0][2] == [("rfqLinkId", "client1")]
    assert native.calls[1][2] == [("quoteId", "quote-1")]
    assert native.calls[2][1] == "accept_other_rfq_quote"
    assert native.calls[3][2] == [("rfqId", "rfq-1"), ("traderType", "request")]
    assert native.calls[4][2] == [("status", "Failed"), ("cursor", "next")]
