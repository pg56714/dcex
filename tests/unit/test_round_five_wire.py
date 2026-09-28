"""Regression coverage through public clients and local HTTP transport."""

import importlib
import inspect
import json
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
