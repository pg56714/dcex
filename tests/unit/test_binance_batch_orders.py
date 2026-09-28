"""Offline coverage for binance batch orders."""

import inspect
import json
from contextlib import asynccontextmanager
from decimal import Decimal
from urllib.parse import parse_qsl, urlsplit

import pytest

from dcex.async_support.binance.client import Client as AsyncClient
from dcex.binance.client import Client
from tests.unit.native_http_helpers import _http_server

CONDITIONAL_TYPES = [
    "STOP",
    "STOP_MARKET",
    "TAKE_PROFIT",
    "TAKE_PROFIT_MARKET",
    "TRAILING_STOP_MARKET",
]


@asynccontextmanager
async def batch_client(asynchronous, base):
    import dcex._native as native

    client = (AsyncClient if asynchronous else Client)(
        api_key="key", api_secret="secret", preload_product_table=False
    )
    if asynchronous:
        await client.async_init()
    client._native_client = native.BinanceHttpClient(
        api_key="key",
        api_secret="secret",
        timeout=2,
        spot_base_url=base,
        futures_base_url=base,
        coin_futures_base_url=base,
        options_base_url=base,
    )
    try:
        yield client
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result


async def invoke(client, method, **kwargs):
    result = getattr(client, method)(**kwargs)
    return await result if inspect.isawaitable(result) else result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("coin", [False, True], ids=["usd-m", "coin-m"])
@pytest.mark.parametrize("kind", CONDITIONAL_TYPES)
async def test_conditional_batch_rejected_before_any_transport(asynchronous, coin, kind):
    method = "place_coin_futures_batch_orders" if coin else "place_futures_batch_orders"
    symbol = "BTCUSD_PERP" if coin else "BTCUSDT"
    entry = {
        "symbol": symbol,
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": "1",
        "price": "50000",
    }
    protective = {"symbol": symbol, "side": "SELL", "type": kind, "quantity": "1"}
    if kind == "TRAILING_STOP_MARKET":
        protective["callbackRate"] = "1"
    else:
        protective["stopPrice"] = "49000"
    if kind in {"STOP", "TAKE_PROFIT"}:
        protective["price"] = "49000"
    expected = "/dapi/v1/algoOrder" if coin else "place_futures_algo_order"
    with _http_server() as (base, received):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(ValueError, match=expected):
                await invoke(client, method, orders=[entry, protective])
        assert received.empty(), "An invalid mixed batch must not even start time synchronization"


BATCH_METHODS = [
    f"{action}_{market}_batch_orders"
    for action in ("place", "amend", "cancel")
    for market in ("futures", "coin_futures")
] + ["place_options_batch_orders", "cancel_options_batch_orders"]


def batch_kwargs(method):
    coin = "coin" in method
    if "options" in method:
        if method.startswith("cancel"):
            return {"product_symbol": "BTC-260925-50000-C", "orderIds": [1, 2]}
        return {
            "orders": [
                {
                    "symbol": "BTC-260925-50000-C",
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": "1",
                    "price": "1",
                    "timeInForce": "GTC",
                }
            ]
        }
    if method.startswith("cancel"):
        return (
            {"symbol": "BTCUSD_PERP", "order_ids": [1, 2]}
            if coin
            else {"product_symbol": "BTC-USDT-SWAP", "order_ids": [1, 2]}
        )
    order = {
        "symbol": "BTCUSD_PERP" if coin else "BTCUSDT",
        "side": "BUY",
        "quantity": "0.1",
        "price": "50000",
    }
    if method.startswith("place"):
        order.update(type="LIMIT", timeInForce="GTC")
    else:
        order["orderId"] = 1
    return {"orders": [order]}


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("method", BATCH_METHODS)
@pytest.mark.parametrize(
    "outcomes",
    [
        [{"orderId": 1, "status": "CANCELED"}, {"code": -2011, "msg": "Unknown order sent."}],
        [{"orderId": 1}, {"orderId": 2}],
        [{"code": -2011, "msg": "Unknown order sent."}, {"code": -2022, "msg": "Rejected"}],
    ],
)
async def test_batch_results_separate_successes_and_failures(asynchronous, method, outcomes):
    kwargs = batch_kwargs(method)
    if "orders" in kwargs:
        second = dict(kwargs["orders"][0])
        if "orderId" in second:
            second["orderId"] = 2
        kwargs["orders"].append(second)
    with _http_server(response_payload=outcomes) as (base, _):
        async with batch_client(asynchronous, base) as client:
            result = await invoke(client, method, **kwargs)
    expected = {"ok": [], "errors": []}
    for index, item in enumerate(outcomes):
        expected["errors" if "code" in item else "ok"].append({"index": index, "response": item})
    assert result == expected


DECIMAL_FIELDS = ["quantity", "price", "stopPrice", "activationPrice", "callbackRate"]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("method", [m for m in BATCH_METHODS if not m.startswith("cancel")])
@pytest.mark.parametrize("field", DECIMAL_FIELDS)
async def test_batch_rejects_float_before_transport(asynchronous, method, field):
    kwargs = batch_kwargs(method)
    kwargs["orders"][0][field] = 0.1
    with _http_server() as (base, received):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(ValueError, match="decimal"):
                await invoke(client, method, **kwargs)
        assert received.empty()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("method", [m for m in BATCH_METHODS if not m.startswith("cancel")])
async def test_batch_serializes_decimal_losslessly(asynchronous, method):
    kwargs = batch_kwargs(method)
    order = kwargs["orders"][0]
    order["quantity"] = Decimal("1E-8")
    order["price"] = Decimal("12345678901234567890.12345678901234567890")
    with _http_server(response_payload=[{"orderId": 1}]) as (base, received):
        async with batch_client(asynchronous, base) as client:
            await invoke(client, method, **kwargs)
        requests = list(received.queue)
    request = next(r for r in requests if "batchOrders" in r["path"])
    query = dict(parse_qsl(urlsplit(request["path"]).query or request["body"]))
    sent = json.loads(query["orders"] if "options" in method else query["batchOrders"])[0]
    assert sent["quantity"] == "0.00000001"
    assert sent["price"] == "12345678901234567890.12345678901234567890"
    assert order["quantity"] == Decimal("1E-8"), "Do not mutate caller input"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("value", ["1e-5", "0", "-1", "NaN", "inf", " 1", "1.2.3"])
async def test_non_plain_decimal_strings_rejected_before_transport(asynchronous, value):
    kwargs = batch_kwargs("place_futures_batch_orders")
    kwargs["orders"][0]["quantity"] = value
    with _http_server() as (base, received):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(ValueError, match="decimal string"):
                await invoke(client, "place_futures_batch_orders", **kwargs)
        assert received.empty()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_batch_top_level_error_still_raises(asynchronous):
    from dcex.utils.errors import FailedRequestError

    with _http_server(response_payload={"code": -2015, "msg": "Invalid API-key"}) as (base, _):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(FailedRequestError, match="-2015"):
                await invoke(
                    client,
                    "cancel_futures_batch_orders",
                    **batch_kwargs("cancel_futures_batch_orders"),
                )


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("outcomes", [{"unexpected": True}, [None]])
async def test_malformed_batch_response_is_not_success(asynchronous, outcomes):
    from dcex.utils.errors import FailedRequestError

    with _http_server(response_payload=outcomes) as (base, _):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(FailedRequestError, match="batch response"):
                await invoke(
                    client,
                    "cancel_futures_batch_orders",
                    **batch_kwargs("cancel_futures_batch_orders"),
                )
