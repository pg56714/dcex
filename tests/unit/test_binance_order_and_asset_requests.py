"""Offline coverage for binance order and asset requests."""
# ruff: noqa: ANN001, ANN201, D103


from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_binance_batch_orders import batch_client, batch_kwargs, invoke


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_binance_partial_cancel_replace_has_structured_outcomes(asynchronous):
    from dcex.utils.errors import FailedRequestError

    outcomes = {
        "cancelResult": "SUCCESS",
        "newOrderResult": "FAILURE",
        "cancelResponse": {"orderId": 1},
        "newOrderResponse": {"code": -2010, "msg": "Rejected"},
    }
    with _http_server({"code": -2021, "msg": "Partial failure", "data": outcomes}, 409) as (
        base,
        _,
    ):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(FailedRequestError) as caught:
                await invoke(
                    client,
                    "cancel_replace_spot_order",
                    product_symbol="BTC-USDT-SPOT",
                    side="BUY",
                    order_type="MARKET",
                    cancel_replace_mode="ALLOW_FAILURE",
                    quantity="1",
                    cancel_order_id=1,
                )
            assert caught.value.response_data == outcomes


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "method,kwargs,path",
    [
        ("wallet_dust_transfer", {"asset": ["ETH", "LTC"]}, "/sapi/v1/asset/dust"),
        (
            "place_spot_sor_order",
            {"symbol": "BTCUSDT", "side": "BUY", "order_type": "MARKET", "quantity": "1"},
            "/api/v3/sor/order",
        ),
        ("sign_futures_tradfi_perps_contract", {}, "/fapi/v1/stock/contract"),
        ("liquidate_margin_account", {"kind_type": "MARGIN"}, "/sapi/v1/margin/manual-liquidation"),
        (
            "set_coin_futures_leverage",
            {"product_symbol": "BTCUSD_PERP", "leverage": 3},
            "/dapi/v1/leverage",
        ),
        (
            "amend_futures_batch_orders",
            {
                "orders": [
                    {
                        "symbol": "BTCUSDT",
                        "side": "BUY",
                        "quantity": "1",
                        "price": "10",
                        "orderId": 1,
                    }
                ]
            },
            "/fapi/v1/batchOrders",
        ),
    ],
)
async def test_binance_order_and_asset_names_and_fields(asynchronous, method, kwargs, path):
    payload = [{"orderId": 1}] if "batch" in method else {"ok": True}
    with _http_server(payload) as (base, received):
        async with batch_client(asynchronous, base) as client:
            await invoke(client, method, **kwargs)
        request = next(r for r in list(received.queue) if urlsplit(r["path"]).path == path)
    pairs = parse_qsl(urlsplit(request["path"]).query or request["body"])
    if method == "wallet_dust_transfer":
        assert [v for k, v in pairs if k == "asset"] == ["ETH,LTC"]
    if method == "set_coin_futures_leverage":
        assert dict(pairs)["symbol"] == "BTCUSD_PERP"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "method,verb",
    [("get_listen_key", "POST"), ("keep_alive_listen_key", "PUT"), ("close_listen_key", "DELETE")],
)
async def test_binance_listen_key_alias_wire(asynchronous, method, verb):
    with _http_server({"listenKey": "key1"}) as (base, received):
        async with batch_client(asynchronous, base) as client:
            result = await invoke(
                client, method, **{} if method == "get_listen_key" else {"listen_key": "key1"}
            )
        request = received.get_nowait()
        assert received.empty()
        assert request["method"] == verb
        assert request["path"] == "/fapi/v1/listenKey"
        assert request["body"] == ""
        assert request["api_key"] == "key"
        assert result == ("key1" if method == "get_listen_key" else {"listenKey": "key1"})


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("action,verb", [("place", "POST"), ("cancel", "DELETE"), ("get", "GET")])
async def test_coin_algo_passthrough_wire(asynchronous, action, verb):
    import hashlib
    import hmac

    fields = {"symbol": "BTCUSD_PERP", "algoId": "123"}
    if action == "place":
        fields = {
            "symbol": "BTCUSD_PERP",
            "side": "SELL",
            "type": "STOP_MARKET",
            "quantity": "1",
            "triggerPrice": "49000",
        }
    with _http_server() as (base, received):
        async with batch_client(asynchronous, base) as client:
            await invoke(client, action + "_coin_futures_algo_order", fields=fields)
        requests = [received.get_nowait() for _ in range(received.qsize())]
    request = next(r for r in requests if not urlsplit(r["path"]).path.endswith("/time"))
    assert request["method"] == verb
    assert urlsplit(request["path"]).path == "/dapi/v1/algoOrder"
    query = request["body"] if verb == "POST" else urlsplit(request["path"]).query
    values = dict(parse_qsl(query))
    signature = values.pop("signature")
    assert (
        signature
        == hmac.new(
            b"secret", query.rsplit("&signature=", 1)[0].encode(), hashlib.sha256
        ).hexdigest()
    )
    assert values.pop("timestamp").isdigit()
    values.pop("recvWindow", None)
    assert values == fields
    if verb != "POST":
        assert request["body"] == ""
    assert request["api_key"] == "key"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "method", ["amend_futures_batch_orders", "amend_coin_futures_batch_orders"]
)
async def test_batch_amend_rejects_undocumented_reduce_only(asynchronous, method):
    kwargs = batch_kwargs(method)
    kwargs["orders"][0]["reduceOnly"] = True
    with _http_server() as (base, received):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(ValueError, match="unsupported order field"):
                await invoke(client, method, **kwargs)
        assert received.empty()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "method,kwargs",
    [
        ("set_coin_futures_leverage", {"product_symbol": "BTCUSDT", "leverage": 3}),
        ("cancel_coin_futures_batch_orders", {"product_symbol": "BTCUSDT", "order_ids": [1]}),
        (
            "place_coin_futures_batch_orders",
            {
                "orders": [
                    {"product_symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "1"}
                ]
            },
        ),
    ],
)
async def test_coin_m_rejects_native_usdt_symbol(asynchronous, method, kwargs):
    with _http_server() as (base, received):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(ValueError, match="market"):
                await invoke(client, method, **kwargs)
        assert received.empty()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_options_mmp_zero_matches_official_inclusive_minimum(asynchronous):
    from tests.unit.test_binance_risk_endpoints import test_risk_wire

    await test_risk_wire(
        asynchronous,
        "set_options_mmp_config",
        {
            "underlying": "BTCUSDT",
            "window_time": 0,
            "frozen_time": 0,
            "qty_limit": "1",
            "delta_limit": "2.5",
        },
        "POST",
        "/eapi/v1/mmpSet",
        {
            "underlying": "BTCUSDT",
            "windowTimeInMilliseconds": "0",
            "frozenTimeInMilliseconds": "0",
            "qtyLimit": "1",
            "deltaLimit": "2.5",
        },
        True,
        False,
    )
