"""Native wire coverage for Binance order lifecycle and risk controls."""

# ruff: noqa: ANN401, D103
from __future__ import annotations

import hashlib
import hmac
import inspect
import json
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from dcex.async_support.binance.client import Client as AsyncClient
from dcex.binance.client import Client
from tests.unit.native_http_helpers import _http_server

CASES = [
    ("create_coin_futures_listen_key", {}, "/dapi/v1/listenKey", {}),
    ("keep_alive_coin_futures_listen_key", {}, "/dapi/v1/listenKey", {}),
    ("close_coin_futures_listen_key", {}, "/dapi/v1/listenKey", {}),
    ("create_pm_listen_key", {}, "/papi/v1/listenKey", {}),
    ("keep_alive_pm_listen_key", {}, "/papi/v1/listenKey", {}),
    ("close_pm_listen_key", {}, "/papi/v1/listenKey", {}),
    (
        "cancel_replace_spot_order",
        {
            "product_symbol": "BTC-USDT-SPOT",
            "side": "BUY",
            "order_type": "LIMIT",
            "cancel_replace_mode": "STOP_ON_FAILURE",
            "quantity": "1",
            "price": "100",
            "time_in_force": "GTC",
            "cancel_order_id": 123,
        },
        "/api/v3/order/cancelReplace",
        {
            "symbol": "BTCUSDT",
            "type": "LIMIT",
            "cancelReplaceMode": "STOP_ON_FAILURE",
            "cancelOrderId": "123",
        },
    ),
    (
        "place_futures_batch_orders",
        {
            "orders": [
                {
                    "product_symbol": "BTC-USDT-SWAP",
                    "side": "BUY",
                    "quantity": "1",
                    "priceMatch": "OPPONENT",
                    "type": "LIMIT",
                    "timeInForce": "GTC",
                }
            ]
        },
        "/fapi/v1/batchOrders",
        {
            "batchOrders": [
                {
                    "side": "BUY",
                    "quantity": "1",
                    "priceMatch": "OPPONENT",
                    "type": "LIMIT",
                    "timeInForce": "GTC",
                    "symbol": "BTCUSDT",
                }
            ]
        },
    ),
    (
        "amend_futures_batch_orders",
        {
            "orders": [
                {
                    "product_symbol": "BTC-USDT-SWAP",
                    "side": "BUY",
                    "quantity": "1",
                    "priceMatch": "OPPONENT",
                    "orderId": 123,
                }
            ]
        },
        "/fapi/v1/batchOrders",
        {
            "batchOrders": [
                {
                    "side": "BUY",
                    "quantity": "1",
                    "priceMatch": "OPPONENT",
                    "orderId": 123,
                    "symbol": "BTCUSDT",
                }
            ]
        },
    ),
    (
        "cancel_futures_batch_orders",
        {"product_symbol": "BTC-USDT-SWAP", "order_ids": [123, 456]},
        "/fapi/v1/batchOrders",
        {"symbol": "BTCUSDT", "orderIdList": [123, 456]},
    ),
    (
        "amend_futures_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "side": "BUY",
            "quantity": "1",
            "price_match": "QUEUE",
            "order_id": 123,
        },
        "/fapi/v1/order",
        {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "quantity": "1",
            "priceMatch": "QUEUE",
            "orderId": "123",
        },
    ),
    (
        "place_coin_futures_batch_orders",
        {
            "orders": [
                {
                    "symbol": "BTCUSD_PERP",
                    "side": "BUY",
                    "quantity": "1",
                    "priceMatch": "OPPONENT",
                    "type": "LIMIT",
                    "timeInForce": "GTC",
                }
            ]
        },
        "/dapi/v1/batchOrders",
        {
            "batchOrders": [
                {
                    "symbol": "BTCUSD_PERP",
                    "side": "BUY",
                    "quantity": "1",
                    "priceMatch": "OPPONENT",
                    "type": "LIMIT",
                    "timeInForce": "GTC",
                }
            ]
        },
    ),
    (
        "amend_coin_futures_batch_orders",
        {
            "orders": [
                {
                    "symbol": "BTCUSD_PERP",
                    "side": "BUY",
                    "quantity": "1",
                    "priceMatch": "OPPONENT",
                    "orderId": 123,
                }
            ]
        },
        "/dapi/v1/batchOrders",
        {
            "batchOrders": [
                {
                    "symbol": "BTCUSD_PERP",
                    "side": "BUY",
                    "quantity": "1",
                    "priceMatch": "OPPONENT",
                    "orderId": 123,
                }
            ]
        },
    ),
    (
        "cancel_coin_futures_batch_orders",
        {"product_symbol": "BTCUSD_PERP", "order_ids": [123, 456]},
        "/dapi/v1/batchOrders",
        {"symbol": "BTCUSD_PERP", "orderIdList": [123, 456]},
    ),
    (
        "amend_coin_futures_order",
        {
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "quantity": "1",
            "price_match": "QUEUE",
            "order_id": 123,
        },
        "/dapi/v1/order",
        {
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "quantity": "1",
            "priceMatch": "QUEUE",
            "orderId": "123",
        },
    ),
    ("get_spot_order_list", {"order_list_id": 1}, "/api/v3/orderList", {"orderListId": "1"}),
    ("get_spot_all_order_lists", {"limit": 20}, "/api/v3/allOrderList", {"limit": "20"}),
    ("get_spot_open_order_lists", {}, "/api/v3/openOrderList", {}),
    (
        "cancel_spot_order_list",
        {"product_symbol": "BTC-USDT-SPOT", "list_client_order_id": "list-1"},
        "/api/v3/orderList",
        {"symbol": "BTCUSDT", "listClientOrderId": "list-1"},
    ),
    (
        "amend_spot_order_keep_priority",
        {
            "product_symbol": "BTC-USDT-SPOT",
            "new_quantity": "0.1",
            "order_id": 1,
            "recv_window": "5000.125",
        },
        "/api/v3/order/amend/keepPriority",
        {"symbol": "BTCUSDT", "newQty": "0.1", "orderId": "1", "recvWindow": "5000.125"},
    ),
    ("get_futures_position_mode", {}, "/fapi/v1/positionSide/dual", {}),
    (
        "set_futures_position_mode",
        {"dual_side_position": True},
        "/fapi/v1/positionSide/dual",
        {"dualSidePosition": "true"},
    ),
    (
        "set_futures_margin_type",
        {"product_symbol": "BTC-USDT-SWAP", "margin_type": "ISOLATED"},
        "/fapi/v1/marginType",
        {"symbol": "BTCUSDT", "marginType": "ISOLATED"},
    ),
    (
        "set_futures_cancel_countdown",
        {"product_symbol": "BTC-USDT-SWAP", "countdown_time": 0},
        "/fapi/v1/countdownCancelAll",
        {"symbol": "BTCUSDT", "countdownTime": "0"},
    ),
    (
        "get_futures_leverage_brackets",
        {"product_symbol": "BTC-USDT-SWAP"},
        "/fapi/v1/leverageBracket",
        {"symbol": "BTCUSDT"},
    ),
    (
        "amend_futures_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "side": "BUY",
            "quantity": "1",
            "price": "60000",
            "order_id": 42,
        },
        "/fapi/v1/order",
        {"symbol": "BTCUSDT", "side": "BUY", "quantity": "1", "price": "60000", "orderId": "42"},
    ),
    ("get_coin_futures_position_mode", {}, "/dapi/v1/positionSide/dual", {}),
    (
        "set_coin_futures_position_mode",
        {"dual_side_position": True},
        "/dapi/v1/positionSide/dual",
        {"dualSidePosition": "true"},
    ),
    (
        "set_coin_futures_margin_type",
        {"product_symbol": "BTCUSD_PERP", "margin_type": "ISOLATED"},
        "/dapi/v1/marginType",
        {"symbol": "BTCUSD_PERP", "marginType": "ISOLATED"},
    ),
    (
        "set_coin_futures_cancel_countdown",
        {"product_symbol": "BTCUSD_PERP", "countdown_time": 0},
        "/dapi/v1/countdownCancelAll",
        {"symbol": "BTCUSD_PERP", "countdownTime": "0"},
    ),
    (
        "get_coin_futures_leverage_brackets",
        {"symbol": "BTCUSD_PERP"},
        "/dapi/v2/leverageBracket",
        {"symbol": "BTCUSD_PERP"},
    ),
    (
        "amend_coin_futures_order",
        {"symbol": "BTCUSD_PERP", "side": "BUY", "quantity": "1", "price": "60000", "order_id": 42},
        "/dapi/v1/order",
        {
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "quantity": "1",
            "price": "60000",
            "orderId": "42",
        },
    ),
    (
        "set_coin_futures_leverage",
        {"product_symbol": "BTCUSD_PERP", "leverage": 5},
        "/dapi/v1/leverage",
        {"symbol": "BTCUSD_PERP", "leverage": "5"},
    ),
    (
        "get_coin_futures_pair_leverage_brackets",
        {"pair": "BTCUSD"},
        "/dapi/v1/leverageBracket",
        {"pair": "BTCUSD"},
    ),
    (
        "get_coin_futures_all_orders",
        {"symbol": "BTCUSD_PERP", "limit": 20},
        "/dapi/v1/allOrders",
        {"symbol": "BTCUSD_PERP", "limit": "20"},
    ),
    (
        "get_coin_futures_account_trades",
        {"symbol": "BTCUSD_PERP", "limit": 20},
        "/dapi/v1/userTrades",
        {"symbol": "BTCUSD_PERP", "limit": "20"},
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(("method", "kwargs", "path", "expected"), CASES, ids=[c[0] for c in CASES])
async def test_controls_sign_and_encode_native_requests(
    asynchronous: bool, method: str, kwargs: dict[str, Any], path: str, expected: dict[str, Any]
) -> None:
    import dcex._native as native

    is_batch = method.endswith("batch_orders")
    payload = [{"orderId": 123}] if is_batch else {"ok": True}
    with _http_server(response_payload=payload) as (base, received):
        cls = AsyncClient if asynchronous else Client
        client = cls(api_key="api-key", api_secret="api-secret", preload_product_table=False)
        if asynchronous:
            await client.async_init()
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="api-secret",
            timeout=10,
            spot_base_url=base,
            futures_base_url=base,
            coin_futures_base_url=base,
            portfolio_margin_base_url=base,
        )
        try:
            result = getattr(client, method)(**kwargs)
            if inspect.isawaitable(result):
                result = await result
            assert result == (
                {"ok": [{"index": 0, "response": {"orderId": 123}}], "errors": []}
                if is_batch
                else {"ok": True}
            )
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        requests = []
        while not received.empty():
            req = received.get_nowait()
            if not urlsplit(req["path"]).path.endswith("/time"):
                requests.append(req)
        assert len(requests) == 1
        request = requests[0]
    split = urlsplit(request["path"])
    assert split.path == path
    if method.endswith("batch_orders"):
        assert (
            request["method"]
            == {"place": "POST", "amend": "PUT", "cancel": "DELETE"}[method.split("_")[0]]
        )
    payload = split.query or request["body"]
    values = dict(parse_qsl(payload))
    for key, value in expected.items():
        assert (
            json.loads(values[key]) if isinstance(value, (list, dict)) else values[key]
        ) == value
    assert "product_symbol" not in values
    assert request["api_key"] == "api-key"
    if method.endswith("listen_key"):
        assert not values
        return
    signed, signature = payload.rsplit("&signature=", 1)
    assert signature == hmac.new(b"api-secret", signed.encode(), hashlib.sha256).hexdigest()


@pytest.mark.parametrize(
    ("method", "kwargs", "message"),
    [
        ("place_futures_batch_orders", {"orders": []}, "1..=5"),
        (
            "cancel_futures_batch_orders",
            {"product_symbol": "BTC-USDT-SWAP", "order_ids": []},
            "1..=10",
        ),
        (
            "cancel_coin_futures_batch_orders",
            {"product_symbol": "BTCUSD_PERP", "order_ids": [1], "client_order_ids": ["id"]},
            "exactly one",
        ),
        (
            "amend_futures_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "side": "BUY",
                "quantity": "1",
                "price": "1",
                "price_match": "QUEUE",
                "order_id": 1,
            },
            "exclusively",
        ),
        (
            "amend_spot_order_keep_priority",
            {"product_symbol": "BTC-USDT-SPOT", "new_quantity": "0.1"},
            "orderId",
        ),
        (
            "set_futures_cancel_countdown",
            {"product_symbol": "BTC-USDT-SWAP", "countdown_time": -1},
            "countdownTime",
        ),
        ("set_coin_futures_leverage", {"product_symbol": "BTCUSD_PERP", "leverage": 126}, "leverage"),
        ("get_spot_all_order_lists", {"from_id": 1, "start_time": 1}, "fromId"),
        (
            "set_futures_margin_type",
            {"product_symbol": "BTC-USDT-SPOT", "margin_type": "ISOLATED"},
            "market",
        ),
    ],
)
def test_controls_reject_invalid_inputs_before_transport(
    method: str, kwargs: dict[str, Any], message: str
) -> None:
    import dcex._native as native

    client = Client(api_key="api-key", api_secret="api-secret", preload_product_table=False)
    client._native_client = native.BinanceHttpClient(
        api_key="api-key",
        api_secret="api-secret",
        timeout=10,
        spot_base_url="http://127.0.0.1:9",
        futures_base_url="http://127.0.0.1:9",
        coin_futures_base_url="http://127.0.0.1:9",
    )
    try:
        with pytest.raises(Exception, match=message):
            getattr(client, method)(**kwargs)
    finally:
        client.close()
