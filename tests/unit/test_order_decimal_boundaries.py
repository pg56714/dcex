"""Documented order decimal boundaries through actual localhost wire requests."""

import importlib
import inspect
import json
from urllib.parse import parse_qs

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_round_seven_wire import close
from tests.unit.test_round_six_wire import invoke

RATIO_CASES = [
    (method, field, value)
    for method in ["place_order", "place_batch_orders", "amend_order", "amend_algo_order", "amend_multiple_orders"]
    for field, value in ([("tpTriggerRatio", "-0.1")] if method.startswith("place") else [("newTpTriggerRatio", "-0.1"), ("newTpTriggerRatio", "0"), ("newSlTriggerRatio", "0")])
]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("method,field,value", RATIO_CASES)
async def test_okx_signed_and_deleted_attached_ratios_reach_wire(asynchronous, native, method, field, value):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.okx.client").Client
    attached = [{"attachAlgoId": "2", field: value}]
    if method == "amend_order":
        args = dict(product_symbol="BTC-USDT-SWAP", ordId="1", attachAlgoOrds=attached)
    elif method == "amend_algo_order":
        args = dict(product_symbol="BTC-USDT-SWAP", algo_id="1", attach_algo_ords=attached)
    elif method == "amend_multiple_orders":
        args = {"orders": [dict(instId="BTC-USDT-SWAP", ordId="1", attachAlgoOrds=attached)]}
    else:
        order = dict(tdMode="cross", side="sell", ordType="limit", sz="1", px="60000", attachAlgoOrds=attached)
        args = dict(product_symbol="BTC-USDT-SWAP", **order) if method == "place_order" else {"orders": [dict(instId="BTC-USDT-SWAP", **order)]}
    with _http_server({"code": "0", "data": []}) as (base, received):
        client = cls(api_key="key", api_secret="secret", passphrase="pass", base_api=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            for invalid in ["-1", "-1.000000000000000001", "1e-7", 0.1]:
                attached[0][field] = invalid
                with pytest.raises(ValueError, match="decimal"):
                    await invoke(client, method, args, native)
                assert received.empty()
            attached[0][field] = value
            if method.startswith("amend"):
                attached[0]["newSz"] = "1e-7"
                with pytest.raises(ValueError, match="unsupported"):
                    await invoke(client, method, args, native)
                assert received.empty()
                del attached[0]["newSz"]
            await invoke(client, method, args, native)
            payload = json.loads(received.get(timeout=10)["body"])
            if isinstance(payload, list):
                payload = payload[0]
            assert payload["attachAlgoOrds"][0][field] == value
        finally:
            await close(client)


KRAKEN_METHODS = [
    "place_spot_market_order", "place_spot_market_buy_order", "place_spot_market_sell_order",
    "place_spot_limit_order", "place_spot_limit_buy_order", "place_spot_limit_sell_order",
    "place_spot_post_only_limit_order", "place_spot_post_only_limit_buy_order", "place_spot_post_only_limit_sell_order", "edit_spot_order",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("method", KRAKEN_METHODS)
async def test_kraken_convenience_zero_volume_never_reaches_wire(asynchronous, native, method):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.kraken.client").Client
    with _http_server({"error": [], "result": {}}) as (base, received):
        client = cls(api_key="key", api_secret="c2VjcmV0", base_url=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            parameters = inspect.signature(getattr(client, method)).parameters
            args = dict(product_symbol="XBTUSD", volume="0")
            if "side" in parameters:
                args["side"] = "buy"
            if "limit" in method:
                args["price"] = "60000"
            if method == "edit_spot_order":
                args["txid"] = "order-1"
                args["pair"] = args.pop("product_symbol")
            with pytest.raises(ValueError, match="positive plain decimal"):
                await invoke(client, method, args, native)
            assert received.empty()
            args["volume"] = "0.125"
            await invoke(client, method, args, native)
            assert parse_qs(received.get(timeout=10)["body"])["volume"] == ["0.125"]
        finally:
            await close(client)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("exchange,method", [("okx", "place_order"), ("okx", "place_batch_orders"), ("kraken", "place_spot_order")])
async def test_zero_limit_price_rejected_before_wire(asynchronous, native, exchange, method):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    kwargs = dict(api_key="key", api_secret="c2VjcmV0", preload_product_table=False)
    if exchange == "okx":
        kwargs["passphrase"] = "pass"
        order = dict(tdMode="cash", side="buy", ordType="limit", sz="1", px="0")
        args = dict(product_symbol="BTC-USDT", **order) if method == "place_order" else {"orders": [dict(instId="BTC-USDT", **order)]}
        target, field = (args if method == "place_order" else args["orders"][0]), "px"
        response = {"code": "0", "data": []}
    else:
        args = dict(product_symbol="XBTUSD", side="buy", ordertype="limit", volume="1", price="0")
        target, field = args, "price"
        response = {"error": [], "result": {}}
    with _http_server(response) as (base, received):
        kwargs["base_api" if exchange == "okx" else "base_url"] = base
        client = cls(**kwargs)
        if asynchronous:
            await client.async_init()
        try:
            for invalid in (["0", "0.000", "-1"] if exchange == "okx" else ["0", "0.000"]):
                target[field] = invalid
                with pytest.raises(ValueError, match="decimal"):
                    await invoke(client, method, args, native)
                assert received.empty()
            target[field] = "60000.125"
            await invoke(client, method, args, native)
            request = received.get(timeout=10)
            if exchange == "kraken":
                assert parse_qs(request["body"])[field] == ["60000.125"]
            else:
                payload = json.loads(request["body"])
                assert (payload[0] if isinstance(payload, list) else payload)[field] == "60000.125"
        finally:
            await close(client)
