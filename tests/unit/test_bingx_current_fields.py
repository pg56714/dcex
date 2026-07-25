"""Regression coverage for the current BingX REST parameter surface."""

# ruff: noqa: D103

from __future__ import annotations

import inspect
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)
from tests.unit.native_http_helpers import _http_server

CURRENT_FIELDS = {
    "get_spot_orderbook_v2": {"product_symbol", "depth", "type_"},
    "get_spot_public_trades": {"product_symbol", "limit"},
    "get_spot_ticker": {"product_symbol"},
    "get_asset_transfer_records": {
        "fromAccount",
        "toAccount",
        "transferId",
        "startTime",
        "endTime",
        "pageIndex",
        "pageSize",
        "recvWindow",
    },
    "place_spot_order": {
        "newClientOrderId",
        "quoteOrderQty",
        "stopPrice",
        "recvWindow",
    },
    "cancel_spot_order": {"orderId", "clientOrderID", "cancelRestrictions"},
    "place_swap_order": {
        "quoteOrderQty",
        "workingType",
        "stopLoss",
        "takeProfit",
        "closePosition",
        "stopGuaranteed",
        "positionId",
        "recvWindow",
    },
    "replace_swap_order": {
        "cancelOrderId",
        "cancelClientOrderId",
        "cancelReplaceMode",
        "quoteOrderQty",
        "recvWindow",
    },
    "cancel_swap_all_orders": {"product_symbol", "type_", "recvWindow"},
    "close_swap_all_positions": {"product_symbol", "recvWindow"},
    "get_margin_type": {"product_symbol", "recvWindow"},
    "set_position_mode": {"dualSidePosition", "recvWindow"},
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_bingx_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "bingx")
    async_client = _client_class("async", "bingx")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


def test_sync_bingx_forwards_official_spot_fields() -> None:
    client = _client_class("sync", "bingx")(**_client_kwargs("bingx"))
    calls = _wire_sync(client)

    client.get_spot_orderbook_v2("BTC-USDT-SPOT", depth=50, type_="step2")
    client.place_spot_limit_buy_order(
        "BTC-USDT-SPOT",
        quantity="0.001",
        price="100000",
        newClientOrderId="client_1",
        recvWindow=5_000,
    )

    assert dict(calls[0]["query"]) == {
        "product_symbol": "BTC-USDT-SPOT",
        "type_": "step2",
        "depth": "50",
    }
    assert dict(calls[1]["query"])["newClientOrderId"] == "client_1"
    assert dict(calls[1]["query"])["recvWindow"] == "5000"


@pytest.mark.asyncio
async def test_async_bingx_forwards_current_swap_fields() -> None:
    client = _client_class("async", "bingx")(**_client_kwargs("bingx"))
    calls = _wire_async(client)

    await client.replace_swap_order(
        "BTC-USDT-SWAP",
        cancelReplaceMode="STOP_ON_FAILURE",
        type_="MARKET",
        side="BUY",
        positionSide="BOTH",
        cancelClientOrderId="old-order",
        quoteOrderQty=25,
        recvWindow=5_000,
    )

    query = dict(calls[0]["query"])
    assert query["cancelClientOrderId"] == "old-order"
    assert query["quoteOrderQty"] == "25"
    assert query["recvWindow"] == "5000"


def _native_client(base_url: str) -> object:
    native = pytest.importorskip("dcex._native")
    return native.BingxHttpClient(
        api_key="api-key",
        api_secret="secret",
        timeout=2,
        base_url=base_url,
    )


def test_native_bingx_asset_transfer_uses_current_v1_path() -> None:
    with _http_server({"code": 0, "data": {}}) as (base_url, received):
        client = _native_client(base_url)
        client.private_request_json(
            "asset_transfer",
            [
                ("fromAccount", "sopt"),
                ("toAccount", "USDTMPerp"),
                ("asset", "USDT"),
                ("amount", "1"),
            ],
        )

    request = received.get_nowait()
    assert urlsplit(request["path"]).path == "/openApi/api/asset/v1/transfer"


def test_native_bingx_uses_official_wire_fields() -> None:
    with _http_server({"code": 0, "data": {}}) as (base_url, received):
        client = _native_client(base_url)
        client.private_request_json(
            "place_spot_post_only_buy_order",
            [
                ("product_symbol", "BTC-USDT-SPOT"),
                ("quantity", "0.001"),
                ("price", "100000"),
            ],
        )
        client.private_request_json(
            "get_asset_transfer_records",
            [("tranId", "123")],
        )

    post_only = dict(parse_qsl(urlsplit(received.get_nowait()["path"]).query))
    transfer = dict(parse_qsl(urlsplit(received.get_nowait()["path"]).query))
    assert post_only["timeInForce"] == "PostOnly"
    assert transfer["transferId"] == "123"
    assert "tranId" not in transfer


def test_native_bingx_spot_v2_depth_uses_underscore_symbol() -> None:
    with _http_server({"code": 0, "data": {}}) as (base_url, received):
        client = _native_client(base_url)
        client.public_request_json(
            "get_spot_orderbook_v2",
            [
                ("product_symbol", "BTC-USDT-SPOT"),
                ("depth", "20"),
                ("type_", "step1"),
            ],
        )

    query = dict(parse_qsl(urlsplit(received.get_nowait()["path"]).query))
    assert query == {"depth": "20", "symbol": "BTC_USDT", "type": "step1"}


def test_native_bingx_accepts_current_swap_trigger_order_type() -> None:
    with _http_server({"code": 0, "data": {}}) as (base_url, received):
        client = _native_client(base_url)
        client.private_request_json(
            "test_swap_order",
            [
                ("product_symbol", "BTC-USDT-SWAP"),
                ("side", "BUY"),
                ("positionSide", "BOTH"),
                ("type_", "TRIGGER_MARKET"),
                ("quantity", "0.001"),
                ("stopPrice", "100000"),
            ],
        )

    query = dict(parse_qsl(urlsplit(received.get_nowait()["path"]).query))
    assert query["type"] == "TRIGGER_MARKET"
    assert query["stopPrice"] == "100000"


@pytest.mark.parametrize(
    ("method_name", "params", "message"),
    [
        (
            "cancel_spot_order",
            [("product_symbol", "BTC-USDT-SPOT")],
            "one of orderId, clientOrderID, clientOrderId is required",
        ),
        (
            "cancel_swap_order",
            [("product_symbol", "BTC-USDT-SWAP")],
            "one of orderId, clientOrderId is required",
        ),
        (
            "get_asset_transfer_records",
            [],
            "either transferId or both fromAccount and toAccount",
        ),
        (
            "get_spot_order_history",
            [("pageIndex", "101"), ("pageSize", "100")],
            "pageIndex * pageSize <= 10000",
        ),
        (
            "get_order_history",
            [("startTime", "0"), ("endTime", "604800001")],
            "time range between startTime and endTime is too large",
        ),
    ],
)
def test_native_bingx_rejects_invalid_current_parameters_before_transport(
    method_name: str,
    params: list[tuple[str, str]],
    message: str,
) -> None:
    client = _native_client("http://127.0.0.1:1")

    with pytest.raises(ValueError, match=message.replace("*", r"\*")):
        client.private_request_json(method_name, params)


def test_native_bingx_rejects_more_than_five_batch_orders() -> None:
    client = _native_client("http://127.0.0.1:1")
    orders = '[{"symbol":"BTC-USDT","side":"BUY","type":"MARKET","quantity":"1"}]'
    six_orders = "[" + ",".join([orders[1:-1]] * 6) + "]"

    with pytest.raises(ValueError, match="between 1 and 5 orders"):
        client.private_request_json(
            "place_swap_batch_order",
            [("batchOrders", six_orders)],
        )
