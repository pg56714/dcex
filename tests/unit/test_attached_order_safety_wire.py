"""Attached order safety against captured localhost requests."""

import importlib
import inspect
import json
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_attached_order_wire import invoke
from tests.unit.test_exchange_structure import NATIVE
from tests.unit.rust_dispatch import arms, request_owners


async def close(client):
    result = client.close()
    if inspect.isawaitable(result):
        await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("method", ["amend_order", "amend_algo_order", "amend_multiple_orders", "place_order", "place_batch_orders"])
@pytest.mark.parametrize("field", ["sz", "newCallbackRatio", "newCallbackSpread", "newActivePx"])
async def test_okx_amend_attached_decimal_fields(asynchronous, native, method, field):
    if method.startswith("place") and field.startswith("new"):
        field = field[3].lower() + field[4:]

    def arguments(value):
        attached = [{"attachAlgoId": "2", field: value}]
        if method == "amend_order":
            return dict(product_symbol="BTC-USDT-SWAP", ordId="1", attachAlgoOrds=attached)
        if method == "amend_algo_order":
            return dict(product_symbol="BTC-USDT-SWAP", algo_id="1", attach_algo_ords=attached)
        if method == "amend_multiple_orders":
            return {"orders": [dict(instId="BTC-USDT-SWAP", ordId="1", newSz="1", attachAlgoOrds=attached)]}
        order = dict(tdMode="cash", side="buy", ordType="limit", sz="1", px="60000", attachAlgoOrds=attached)
        if method == "place_order":
            return dict(product_symbol="BTC-USDT", **order)
        return {"orders": [dict(instId="BTC-USDT", **order)]}
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.okx.client").Client
    with _http_server({"code": "0", "data": []}) as (base, received):
        client = cls(api_key="key", api_secret="secret", passphrase="pass", base_api=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            for value in [0.1, "1e-7", "-5", "0"]:
                with pytest.raises(ValueError, match="decimal"):
                    await invoke(client, method, arguments(value), native)
                assert received.empty()
            await invoke(client, method, arguments("0.125"), native)
            payload = json.loads(received.get(timeout=10)["body"])
            if isinstance(payload, list):
                payload = payload[0]
            assert payload["attachAlgoOrds"][0][field] == "0.125"
        finally:
            await close(client)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("value", [[{"stopPrice": "-5"}], 5, True, None, "", "  ", {}, "{}"])
async def test_bingx_batch_attached_object_or_absent(asynchronous, native, value):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.bingx.client").Client
    with _http_server({"code": 0, "data": {}}) as (base, received):
        client = cls(api_key="key", api_secret="secret", base_url=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            order = dict(symbol="BTC-USDT", side="BUY", type="MARKET", positionSide="LONG", quantity="1", takeProfit=value, stopLoss=value)
            args = {"batchOrders" if native else "batch_orders": [order]}
            if value is None or isinstance(value, str) and not value.strip():
                await invoke(client, "place_swap_batch_order", args, native)
                request = received.get(timeout=10)
                params = parse_qs(urlsplit(request["path"]).query or request["body"])
                payload = json.loads(params["batchOrders"][0])[0]
                assert "takeProfit" not in payload
                assert "stopLoss" not in payload
            else:
                with pytest.raises(ValueError, match="JSON object"):
                    await invoke(client, "place_swap_batch_order", args, native)
                assert received.empty()
        finally:
            await close(client)


def test_lighter_funds_submit_only_from_withdrawals():
    source = (NATIVE / "lighter/trade.rs").read_text(encoding="utf-8")
    for names, body in arms(source):
        if set(names) & {"withdraw_l2", "transfer_l2_account", "transfer_same_master_account"}:
            assert "submit_signed_tx" not in body
    owners = request_owners((NATIVE / "lighter/withdrawals.rs").read_text(encoding="utf-8"))
    assert not {"sign_withdrawal_or_approval", "sign_internal_transfer"} & owners


@pytest.mark.parametrize("exchange,method,array,field", [
    ("okx", "place_batch_orders", "orders", "sz"),
    ("bybit", "place_batch_order", "request", "qty"),
    ("bitget", "place_futures_batch_orders", "orderList", "size"),
    ("bingx", "place_swap_batch_order", "batchOrders", "quantity"),
])
def test_batch_zero_sizes_follow_single_order_rules(exchange, method, array, field):
    from dcex._input_codec import CATALOG, normalize
    schema = CATALOG["exchanges"][exchange][method]
    with pytest.raises(ValueError, match="positive plain decimal"):
        normalize({array: [{field: "0"}]}, schema=schema)
    if exchange == "bybit":
        valid = {array: [{field: "0", "reduceOnly": True, "closeOnTrigger": True}]}
        assert normalize(valid, schema=schema) == valid


def test_okx_amend_prices_have_consistent_single_and_batch_rules():
    from dcex._input_codec import CATALOG, normalize
    for method in ["amend_order", "amend_multiple_orders"]:
        for field in ["newPx", "newPxUsd", "newPxVol"]:
            value = {field: "0"}
            if method == "amend_multiple_orders":
                value = {"orders": [value]}
            with pytest.raises(ValueError, match="positive plain decimal"):
                normalize(value, schema=CATALOG["exchanges"]["okx"][method])
