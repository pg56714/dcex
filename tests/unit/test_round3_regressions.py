"""Regression cases for the second review, using real offline HTTP dispatch."""
import inspect
import json
from dataclasses import replace
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.test_binance_batch_review import batch_client, invoke, batch_kwargs
from tests.unit.native_http_helpers import _http_server


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method,verb", [("get_listen_key", "POST"), ("keep_alive_listen_key", "PUT"), ("close_listen_key", "DELETE")])
async def test_binance_listen_key_alias_wire(asynchronous, method, verb):
    with _http_server({"listenKey": "key1"}) as (base, received):
        async with batch_client(asynchronous, base) as client:
            result = await invoke(client, method, **({} if method == "get_listen_key" else {"listen_key": "key1"}))
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
        fields = {"symbol": "BTCUSD_PERP", "side": "SELL", "type": "STOP_MARKET", "quantity": "1", "triggerPrice": "49000"}
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
    assert signature == hmac.new(b"secret", query.rsplit("&signature=", 1)[0].encode(), hashlib.sha256).hexdigest()
    assert values.pop("timestamp").isdigit()
    values.pop("recvWindow", None)
    assert values == fields
    if verb != "POST":
        assert request["body"] == ""
    assert request["api_key"] == "key"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_aster_futures_withdraw_signature_chain_id(asynchronous):
    from tests.unit.test_aster_endpoint_coverage import Client, AsyncClient, _client_kwargs
    fields = dict(chain_id=56, asset="USDT", amount="1", fee="0.1", receiver="0x" + "22" * 20,
                  user_nonce="123", user_signature="0x" + "11" * 65, signature_chain_id="0x38")
    with _http_server() as (base, received):
        client = (AsyncClient if asynchronous else Client)(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            await invoke(client, "withdraw_futures_signed", **fields)
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        requests = [received.get_nowait() for _ in range(received.qsize())]
    request = next(r for r in requests if "user-withdraw" in r["path"])
    assert request["method"] == "POST"
    params = dict(parse_qsl(request["body"] or urlsplit(request["path"]).query))
    assert params["signatureChainId"] == "0x38"
    assert params["userNonce"] == "123"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", ["amend_futures_batch_orders", "amend_coin_futures_batch_orders"])
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
@pytest.mark.parametrize("exchange,method,base_kwargs,id_kwargs,path,verb", [
    ("kucoin", "cancel_spot_stop_orders", {}, {"order_ids": "123,456"}, "/api/v1/stop-order/cancel", "DELETE"),
    ("kucoin", "cancel_spot_oco_orders", {}, {"order_ids": "123,456"}, "/api/v3/oco/orders", "DELETE"),
    ("kucoin", "cancel_margin_oco_orders", {}, {"order_ids": "123,456"}, "/api/v3/hf/margin/oco-order/cancel", "DELETE"),
    ("bitget", "cancel_futures_plan_orders", {"product_type": "USDT-FUTURES"}, {"order_id_list": [{"orderId": "123"}]}, "/api/v2/mix/order/cancel-plan-order", "POST"),
])
@pytest.mark.parametrize("scope", ["ids", "symbol", "conflict"])
async def test_id_scoped_cancel_wire(asynchronous, exchange, method, base_kwargs, id_kwargs, path, verb, scope):
    import importlib
    helper = importlib.import_module(f"tests.unit.test_{exchange}_endpoint_coverage")
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    payload = {"code": "200000" if exchange == "kucoin" else "00000", "data": {}}
    with _http_server(payload) as (base, received):
        config = helper._client_kwargs(base, base) if exchange == "kucoin" else helper._client_kwargs(base)
        client = cls(**config)
        if asynchronous:
            await client.async_init()
        kwargs = dict(base_kwargs)
        if scope == "ids":
            kwargs.update(id_kwargs)
        else:
            kwargs["product_symbol"] = "BTC-USDT-SPOT" if exchange == "kucoin" else "BTC-USDT-SWAP"
        try:
            if scope == "conflict":
                with pytest.raises(ValueError, match="exclusively"):
                    await invoke(client, method, **kwargs, all_symbols=True)
                assert received.empty()
                return
            await invoke(client, method, **kwargs)
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        request = received.get_nowait()
        assert request["method"] == verb
        assert urlsplit(request["path"]).path == path
        fields = json.loads(request["body"]) if exchange == "bitget" else dict(parse_qsl(urlsplit(request["path"]).query))
        assert "all_symbols" not in fields
        if scope == "ids":
            assert "symbol" not in fields
            assert fields["orderIdList" if exchange == "bitget" else "orderIds"] == (id_kwargs.get("order_id_list") or id_kwargs["order_ids"])


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method,kwargs", [
    ("set_coin_futures_leverage", {"product_symbol": "BTCUSDT", "leverage": 3}),
    ("cancel_coin_futures_batch_orders", {"product_symbol": "BTCUSDT", "order_ids": [1]}),
    ("place_coin_futures_batch_orders", {"orders": [{"product_symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "1"}]}),
])
async def test_coin_m_rejects_native_usdt_symbol(asynchronous, method, kwargs):
    with _http_server() as (base, received):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(ValueError, match="market"):
                await invoke(client, method, **kwargs)
        assert received.empty()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("whitelist", [None, "192.0.2.1"])
async def test_aster_withdraw_permission_preserved(asynchronous, whitelist):
    from tests.unit.test_aster_endpoint_coverage import CASES, Client, AsyncClient, _client_kwargs, _assert_request, _drain
    case = next(c for c in CASES if c.method == "register_agent_signed")
    kwargs = dict(case.kwargs, can_withdraw=True)
    params = dict(case.params, canWithdraw="true")
    if whitelist is not None:
        kwargs["ip_whitelist"] = whitelist
        params["ipWhitelist"] = whitelist
    case = replace(case, kwargs=kwargs, params=params, verb="POST")
    with _http_server() as (base, received):
        client = (AsyncClient if asynchronous else Client)(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            if whitelist is None:
                with pytest.raises(ValueError, match="ipWhitelist"):
                    await invoke(client, case.method, **case.kwargs)
                assert received.empty()
                return
            await invoke(client, case.method, **case.kwargs)
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        _assert_request(case, _drain(received))


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_options_mmp_zero_matches_official_inclusive_minimum(asynchronous):
    from tests.unit.test_binance_risk_endpoints import test_risk_wire
    await test_risk_wire(asynchronous, "set_options_mmp_config", {
        "underlying": "BTCUSDT", "window_time": 0, "frozen_time": 0,
        "qty_limit": "1", "delta_limit": "2.5",
    }, "POST", "/eapi/v1/mmpSet", {
        "underlying": "BTCUSDT", "windowTimeInMilliseconds": "0",
        "frozenTimeInMilliseconds": "0", "qtyLimit": "1", "deltaLimit": "2.5",
    }, True, False)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("trade_type,symbol", [("MARGIN", "BTC-USDT-SWAP"), ("FUTURES", "BTC-USDT-SPOT")])
async def test_kucoin_leverage_rejects_market_mismatch(mode, trade_type, symbol):
    import importlib
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs
    module = "dcex.async_support" if mode == "async" else "dcex"
    cls = importlib.import_module(f"{module}.kucoin.client").Client
    with _http_server() as (base, received):
        client = cls(**_client_kwargs(base, base))
        if mode == "async":
            await client.async_init()
        try:
            with pytest.raises(ValueError, match="tradeType"):
                await invoke(client, "get_uta_leverage", trade_type=trade_type, product_symbol=symbol)
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        assert received.empty()
