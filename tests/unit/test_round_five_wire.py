"""Regression coverage through public clients and local HTTP transport."""

import importlib
import inspect
import json
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("case", ["attached", "market_trigger", "batch"])
async def test_round_five_regression_wire(asynchronous, case, monkeypatch):
    exchange = {"attached": "bingx", "market_trigger": "okx", "batch": "bybit"}[case]
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    with _http_server({"code": "0", "retCode": 0, "data": [], "result": {}}) as (base, received):
        options = dict(api_key="key", api_secret="secret", preload_product_table=False)
        if exchange == "bybit":
            manager = importlib.import_module(f"{prefix}.bybit._http_manager")
            monkeypatch.setattr(manager, "HTTP_URL", base)
            options["sync_server_time"] = False
        else:
            options["base_url" if exchange == "bingx" else "base_api"] = base
        if exchange == "okx":
            options["passphrase"] = "pass"
        client = cls(**options)
        if asynchronous:
            await client.async_init()
        async def call(method, **kwargs):
            result = getattr(client, method)(**kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        try:
            if case == "attached":
                attached = '{"type":"TAKE_PROFIT_MARKET","stopPrice":61000.5}'
                await call("place_swap_order", product_symbol="BTC-USDT-SWAP", type_="MARKET", side="BUY", position_side="LONG", quantity="1", take_profit=attached)
                request = received.get(timeout=2)
                assert urlsplit(request["path"]).path == "/openApi/swap/v2/trade/order"
                params = parse_qs(urlsplit(request["path"]).query or request["body"])
                assert json.loads(params["takeProfit"][0]) == json.loads(attached)
            elif case == "market_trigger":
                await call("place_algo_order", product_symbol="BTC-USDT-SWAP", trade_mode="cross", side="buy", order_type="trigger", sz="1", trigger_px="60000", order_px="-1")
                request = received.get(timeout=2)
                assert urlsplit(request["path"]).path == "/api/v5/trade/order-algo"
                assert json.loads(request["body"])["orderPx"] == "-1"
            else:
                order = dict(symbol="BTCUSDT", side="Buy", orderType="Limit", qty="0.1", price="60000")
                await call("place_batch_order", request=[order])
                request = received.get(timeout=2)
                assert urlsplit(request["path"]).path == "/v5/order/create-batch"
                assert json.loads(request["body"])["request"] == [order]
                for field, value in [("qty", 0.1), ("price", "1e-7")]:
                    with pytest.raises(ValueError, match="decimal"):
                        await call("place_batch_order", request=[{**order, field: value}])
                    assert received.empty()
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_bingx_batch_retains_exact_json_numbers(asynchronous):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.bingx.client").Client
    with _http_server({"code": 0, "data": {}}) as (base, received):
        client = cls(api_key="key", api_secret="secret", base_url=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            order = dict(symbol="BTC-USDT", side="BUY", type="LIMIT", positionSide="LONG", quantity="0.123456789012345678901", price="61000.123456789012345678")
            result = client.place_swap_batch_order(batch_orders=[order])
            if inspect.isawaitable(result):
                await result
            request = received.get(timeout=2)
            params = parse_qs(urlsplit(request["path"]).query or request["body"])
            decoded = json.loads(params["batchOrders"][0], parse_float=Decimal)
            assert decoded[0]["quantity"] == Decimal(order["quantity"])
            assert decoded[0]["price"] == Decimal(order["price"])
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_documented_signed_values_reach_the_wire(asynchronous):
    from tests.unit.test_kraken_endpoint_coverage import _client_kwargs, _route_server

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.kraken.client").Client
    with _route_server() as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            result = client.place_futures_order(product_symbol="BTC-USD-SWAP", side="sell", orderType="take_profit", size="1", stopPrice="60000", limitPriceOffsetValue="-0.5", limitPriceOffsetUnit="PERCENT")
            if inspect.isawaitable(result):
                await result
            request = received.get(timeout=2)
            assert parse_qs(request["body"])["limitPriceOffsetValue"] == ["-0.5"]
            # Official batch support is unconfirmed; retain the explicit native error.
            with pytest.raises(ValueError, match="unsupported batch instruction field"):
                result = client.manage_futures_batch_orders(orders=[dict(order="send", order_tag="offset", symbol="PF_XBTUSD", side="sell", orderType="take_profit", size="1", stopPrice="60000", limitPriceOffsetValue="-0.5", limitPriceOffsetUnit="PERCENT")])
                if inspect.isawaitable(result):
                    await result
            assert received.empty()
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
    cls = importlib.import_module(f"{prefix}.okx.client").Client
    with _http_server({"code": "0", "data": []}) as (base, received):
        client = cls(api_key="key", api_secret="secret", passphrase="pass", base_api=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            result = client.simulate_positions(idx_vol="-0.5")
            if inspect.isawaitable(result):
                await result
            assert json.loads(received.get(timeout=2)["body"])["idxVol"] == "-0.5"
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_aster_signed_bbo_offset_reaches_the_wire(asynchronous):
    from tests.unit.test_aster_endpoint_coverage import _client_kwargs

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.aster.client").Client
    with _http_server({"orderId": 1}) as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            result = client.place_futures_order(product_symbol="BTC-USDT-SWAP", side="buy", type_="LIMIT", quantity="1", price="60000", timeInForce="GTC", pegPriceType="QUEUE_1", pegOffset="-0.5")
            if inspect.isawaitable(result):
                await result
            request = received.get(timeout=2)
            assert urlsplit(request["path"]).path == "/fapi/v3/order"
            assert parse_qs(urlsplit(request["path"]).query or request["body"])["pegOffset"] == ["-0.5"]
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
