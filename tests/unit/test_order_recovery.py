"""Offline recovery scenarios for orders accepted before the response is lost."""

from unittest.mock import AsyncMock

import pytest

from tests.stateful_adapters import CexAdapter
from tests.stateful_dex import ExtendedAdapter, HyperliquidAdapter, LighterAdapter, OndoAdapter
from tests.stateful_lifecycle import LifecycleError, run_lifecycle
from tests.unit.test_stateful_adapters import ExchangeMock
from tests.unit.test_stateful_dex import DexMock

CASES = [
    ("binance", "newClientOrderId", "clientOrderId", "orderId"),
    ("aster", "newClientOrderId", "clientOrderId", "orderId"),
    ("bybit", "orderLinkId", "orderLinkId", "orderId"),
    ("okx", "clOrdId", "clOrdId", "ordId"),
    ("bitget", "client_oid", "clientOid", "orderId"),
    ("bingx", "new_client_order_id", "clientOrderID", "orderId"),
    ("mexc", "newClientOrderId", "clientOrderId", "orderId"),
    ("kucoin", "clientOid", "clientOid", "id"),
    ("backpack", "clientId", "clientId", "id"),
    ("kraken", "cl_ord_id", "cl_ord_id", "id"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("spot", [True, False])
@pytest.mark.parametrize("exchange,parameter,field,identifier", CASES)
async def test_cex_lost_response_only_cancels_its_client_id(
    mode, spot, exchange, parameter, field, identifier
):
    if not spot:
        parameter, field, identifier = {
            "bingx": ("client_order_id", "clientOrderId", "orderId"),
            "mexc": ("externalOid", "externalOid", "orderId"),
            "kraken": ("cliOrdId", "cliOrdId", "order_id"),
        }.get(exchange, (parameter, field, identifier))
    client = ExchangeMock(exchange, spot, mode)
    adapter = CexAdapter(
        client, exchange, "spot" if spot else "swap", "BTC-USDT-SPOT" if spot else "BTC-USDT-SWAP"
    )
    original_payload = client.payload

    def lost_response(method, kwargs):
        response = original_payload(method, kwargs)
        if method.startswith("place_"):
            assert str(kwargs[parameter]) == adapter.client_order_id
            raise TimeoutError("accepted but response lost")
        return response

    client.payload = lost_response

    async def open_orders():
        if not client.placed:
            return []
        return [
            {field: "unrelated", identifier: "456"},
            *([] if client.cancelled else [{field: adapter.client_order_id, identifier: "123"}]),
        ]

    adapter.open_orders = open_orders
    result = {}
    with pytest.raises(LifecycleError):
        await run_lifecycle(adapter, result, poll_delay=0)
    cancellations = [kwargs for method, kwargs in client.calls if method.startswith("cancel_")]
    assert len(cancellations) == 1
    assert "456" not in str(cancellations)
    assert result["order_id"] == "123"
    assert result["client_order_id"] == adapter.client_order_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exchange,cls,parameter,field,id_field",
    [
        ("extended", ExtendedAdapter, "external_id", "externalId", "id"),
        ("ondo", OndoAdapter, "clientOrderId", "clientOrderId", "orderId"),
    ],
)
@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_dex_external_id_survives_lost_ack(exchange, cls, parameter, field, id_field, mode):
    client = DexMock(exchange, mode)
    adapter = cls(client, exchange, "swap", "BTC-USD-SWAP")
    plan, _ = await adapter.prepare()
    await adapter.place(plan)
    placement = next(kwargs for method, kwargs in client.calls if method.startswith("place_"))
    assert placement[parameter] == adapter.client_order_id
    adapter.open_orders = AsyncMock(
        return_value=[
            {field: "unrelated", id_field: "456"},
            {field: adapter.client_order_id, id_field: "123"},
        ]
    )
    assert await adapter.recover_order() == "123"
    adapter.open_orders.return_value = [{field: "unrelated", id_field: "456"}]
    assert await adapter.recover_order() is None


@pytest.mark.asyncio
async def test_hyperliquid_recovery_requires_matching_cloid():
    adapter = HyperliquidAdapter(
        DexMock("hyperliquid", "sync"), "hyperliquid", "swap", "BTC-USD-SWAP"
    )
    adapter.call = AsyncMock(
        return_value={
            "status": "order",
            "order": {"order": {"oid": 123, "cloid": adapter.client_order_id}},
        }
    )
    assert await adapter.recover_order() == "123"
    adapter.call.assert_awaited_once_with(
        "order_status", user=adapter.user, oid=adapter.client_order_id
    )
    adapter.call.return_value["order"]["order"]["cloid"] = "unrelated"
    with pytest.raises(LifecycleError, match="different client ID"):
        await adapter.recover_order()


@pytest.mark.asyncio
async def test_lighter_recovery_filters_client_index():
    adapter = LighterAdapter(DexMock("lighter", "sync"), "lighter", "mainnet", "ETH")
    adapter.call = AsyncMock(
        return_value={
            "orders": [
                {"client_order_index": adapter.client_index, "order_index": 123},
                {"client_order_index": adapter.client_index + 1, "order_index": 456},
            ]
        }
    )
    assert await adapter.recover_order() == "123"
    assert int(adapter.client_order_id) == adapter.client_index
