"""Round-six regressions through real public and native localhost requests."""

import importlib
import inspect
import json
from copy import deepcopy
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.input_contract_coverage import missing_wire_declarations
from dcex._input_codec import CATALOG


ATTACHED_AMEND = dict(attachAlgoId="2", sz="0.125", newTpTriggerPx="61000.125", newTpOrdPx="-1", newSlTriggerPx="50000.125", newSlOrdPx="-1")
OKX_CASES = [
    ("amend_multiple_orders", {"orders": [dict(instId="BTC-USDT", ordId="1", newPx="60000.125", newSz="1", newPxUsd="60000.125", newPxVol="0.125", attachAlgoOrds=[ATTACHED_AMEND])]}, "/api/v5/trade/amend-batch-orders"),
    ("amend_order", dict(product_symbol="BTC-USDT", ordId="1", newPx="60000.125", attachAlgoOrds=[ATTACHED_AMEND]), "/api/v5/trade/amend-order"),
    ("amend_algo_order", dict(product_symbol="BTC-USDT", algo_id="1", attach_algo_ords=[ATTACHED_AMEND]), "/api/v5/trade/amend-algos"),
    ("place_batch_orders", {"orders": [dict(instId="BTC-USDT", tdMode="cash", side="buy", ordType="limit", sz="1", px="60000.125", attachAlgoOrds=[dict(tpTriggerPx="61000.125", tpOrdPx="-1", slTriggerPx="50000.125", slOrdPx="-1")])]}, "/api/v5/trade/batch-orders"),
]
OKX_ALIASES = {"algo_id": "algoId", "attach_algo_ords": "attachAlgoOrds"}
DECIMAL_KEYS = {"newPx", "newSz", "newPxUsd", "newPxVol", "newTpTriggerPx", "newTpOrdPx", "newSlTriggerPx", "newSlOrdPx", "tpTriggerPx", "tpOrdPx", "slTriggerPx", "slOrdPx", "sz", "px"}


async def invoke(client, method, kwargs, native=False):
    if native:
        params = [(OKX_ALIASES.get(key, key), json.dumps(value, separators=(",", ":")) if isinstance(value, (dict, list, bool)) else str(value)) for key, value in kwargs.items()]
        result = client._native_private(method, params)
    else:
        result = getattr(client, method)(**kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


def decimal_paths(value, prefix=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in DECIMAL_KEYS:
                yield (*prefix, key)
            yield from decimal_paths(child, (*prefix, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from decimal_paths(child, (*prefix, index))


def changed(value, path, replacement):
    value = deepcopy(value)
    parent = value
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = replacement
    return value


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True], ids=["public", "native"])
@pytest.mark.parametrize("method,kwargs,endpoint", OKX_CASES, ids=[case[0] for case in OKX_CASES])
async def test_okx_actual_batch_and_attached_decimal_fields(asynchronous, native, method, kwargs, endpoint):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.okx.client").Client
    with _http_server({"code": "0", "data": []}) as (base, received):
        client = cls(api_key="key", api_secret="secret", passphrase="pass", base_api=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            await invoke(client, method, kwargs, native)
            request = received.get(timeout=2)
            assert urlsplit(request["path"]).path == endpoint
            payload = json.loads(request["body"])
            contract = CATALOG["exchanges"]["okx"][method]
            wire = {"orders": payload} if isinstance(payload, list) else payload
            assert not missing_wire_declarations(wire, contract)
            expected = deepcopy(kwargs.get("orders", kwargs))
            if isinstance(expected, dict):
                expected["instId"] = expected.pop("product_symbol")
                expected = {OKX_ALIASES.get(key, key): value for key, value in expected.items()}
                for key, value in expected.items():
                    assert payload[key] == value
            else:
                assert payload == expected
            for path in decimal_paths(kwargs):
                for invalid in [0.1, "1e-7", "-5"]:
                    if native and len(path) == 1 and isinstance(invalid, float):
                        # Raw native pairs are already strings. Only the public
                        # boundary can observe a scalar's original Python type.
                        continue
                    with pytest.raises(ValueError, match="decimal"):
                        await invoke(client, method, changed(kwargs, path, invalid), native)
                    assert received.empty(), path
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.parametrize("method,kwargs,endpoint", OKX_CASES, ids=[case[0] for case in OKX_CASES])
def test_okx_completeness_detects_wrong_declared_wire_names(method, kwargs, endpoint):
    wire = {OKX_ALIASES.get(key, key): value for key, value in kwargs.items()}
    original = CATALOG["exchanges"]["okx"][method]
    assert not missing_wire_declarations(wire, original)
    for path in decimal_paths(wire):
        contract = deepcopy(original)
        parent = contract
        for part in path[:-1]:
            parent = parent["items"] if isinstance(part, int) else parent["properties"][part]
        fields = parent["properties"]
        fields["wrong_" + path[-1]] = fields.pop(path[-1])
        expected = tuple("[]" if isinstance(part, int) else part for part in path)
        assert missing_wire_declarations(wire, contract) == [expected]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True], ids=["public", "native"])
@pytest.mark.parametrize("copy_trading", [False, True])
async def test_kucoin_margin_is_a_positive_decimal_on_the_wire(asynchronous, native, copy_trading):
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.kucoin.client").Client
    method = "post_v1_copy_trade_futures_position_margin_deposit_margin" if copy_trading else "add_futures_isolated_margin"
    symbol = dict(symbol="XBTUSDTM") if copy_trading else dict(product_symbol="BTC-USDT-SWAP")
    with _http_server({"code": "200000", "data": {}}) as (base, received):
        client = cls(**_client_kwargs(base, base))
        if asynchronous:
            await client.async_init()
        try:
            kwargs = dict(**symbol, margin="1.25", **({"bizNo": "1"} if native else {"biz_no": "1"}))
            await invoke(client, method, kwargs, native)
            request = received.get(timeout=2)
            assert urlsplit(request["path"]).path == ("/api/v1/copy-trade/futures/position/margin/deposit-margin" if copy_trading else "/api/v1/position/margin/deposit-margin")
            payload = json.loads(request["body"], parse_float=Decimal)
            assert Decimal(str(payload["margin"])) == Decimal("1.25")
            invalid_values = ["1e-7", "-1", "0"] if native else [0.1 + 0.2, "1e-7", "-1", "0"]
            for invalid in invalid_values:
                with pytest.raises(ValueError, match="decimal"):
                    await invoke(client, method, {**kwargs, "margin": invalid}, native)
                assert received.empty()
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True], ids=["public", "native"])
@pytest.mark.parametrize("settle", [False, True])
async def test_kraken_zero_volume_closing_order_reaches_wire(asynchronous, native, settle):
    from tests.unit.test_kraken_endpoint_coverage import _client_kwargs, _route_server

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.kraken.client").Client
    with _route_server() as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            kwargs = dict(product_symbol="BTC-USD", side="sell", ordertype="settle-position" if settle else "market", volume="0", leverage="2")
            if not settle:
                kwargs["reduce_only"] = True
            with pytest.raises(ValueError, match="positive plain decimal"):
                await invoke(client, "place_spot_order", dict(product_symbol="BTC-USD", side="buy", ordertype="limit", price="100", volume="0"), native)
            assert received.empty()
            await invoke(client, "place_spot_order", kwargs, native)
            request = received.get(timeout=2)
            assert urlsplit(request["path"]).path == "/0/private/AddOrder"
            assert parse_qs(request["body"])["volume"] == ["0"]
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True], ids=["public", "native"])
@pytest.mark.parametrize("json_string", [False, True], ids=["object", "json-string"])
async def test_bingx_batch_attached_orders_use_json_strings_with_exact_numbers(asynchronous, native, json_string):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.bingx.client").Client
    with _http_server({"code": 0, "data": {}}) as (base, received):
        client = cls(api_key="key", api_secret="secret", base_url=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            attached = dict(type="TAKE_PROFIT_MARKET", stopPrice="61000.123456789012345678")
            value = json.dumps(attached) if json_string else attached
            order = dict(symbol="BTC-USDT", side="BUY", type="MARKET", positionSide="LONG", quantity="1", takeProfit=value)
            args = {"batchOrders" if native else "batch_orders": [order]}
            await invoke(client, "place_swap_batch_order", args, native)
            request = received.get(timeout=2)
            params = parse_qs(urlsplit(request["path"]).query or request["body"])
            payload = json.loads(params["batchOrders"][0])
            assert isinstance(payload[0]["takeProfit"], str)
            nested = json.loads(payload[0]["takeProfit"], parse_float=Decimal)
            assert nested["stopPrice"] == Decimal(attached["stopPrice"])
            assert "price" not in nested
            for field in ["price", "stopPrice"]:
                bad = {**attached, field: "0"}
                bad_order = {**order, "takeProfit": json.dumps(bad) if json_string else bad}
                with pytest.raises(ValueError, match="decimal"):
                    await invoke(client, "place_swap_batch_order", {next(iter(args)): [bad_order]}, native)
                assert received.empty()
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True], ids=["public", "native"])
@pytest.mark.parametrize("method", ["place_order", "place_market_order", "place_limit_order", "place_batch_orders"])
async def test_backpack_percent_trigger_quantity_reaches_wire(asynchronous, native, method):
    import base64

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.backpack.client").Client
    with _http_server({}) as (base, received):
        client = cls(api_key=base64.b64encode(bytes(32)).decode(), api_secret=base64.b64encode(bytes(32)).decode(), base_url=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            order = dict(product_symbol="BTC-USDC-SWAP", side="Bid", quantity="1", triggerQuantity="50%")
            if method in {"place_order", "place_batch_orders"}:
                order["orderType"] = "Market"
            elif method == "place_limit_order":
                order["price"] = "60000"
            if method == "place_batch_orders":
                order["symbol"] = "BTC_USDC_PERP"
                del order["product_symbol"]
            for invalid in ["0%", "150%", "100.000000000000000001%"]:
                bad = {**order, "triggerQuantity": invalid}
                with pytest.raises(ValueError, match="decimal percentage"):
                    await invoke(client, method, {"orders": [bad]} if method == "place_batch_orders" else bad, native)
                assert received.empty()
            await invoke(client, method, {"orders": [order]} if method == "place_batch_orders" else order, native)
            payload = json.loads(received.get(timeout=2)["body"])
            if method == "place_batch_orders":
                payload = payload[0]
            assert payload["triggerQuantity"] == "50%"
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("native", [False, True], ids=["public", "native"])
async def test_bybit_zero_quantity_requires_both_closing_flags(asynchronous, native, monkeypatch):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    manager = importlib.import_module(f"{prefix}.bybit._http_manager")
    cls = importlib.import_module(f"{prefix}.bybit.client").Client
    with _http_server({"retCode": 0, "result": {}}) as (base, received):
        monkeypatch.setattr(manager, "HTTP_URL", base)
        client = cls(api_key="key", api_secret="secret", sync_server_time=False, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            order = dict(product_symbol="BTC-USDT-SWAP", side="Sell", orderType="Market", qty="0")
            for flags in [{}, {"reduceOnly": True}, {"closeOnTrigger": True}, {"reduceOnly": True, "closeOnTrigger": False}]:
                with pytest.raises(ValueError, match="decimal"):
                    await invoke(client, "place_order", {**order, **flags}, native)
                assert received.empty()
            await invoke(client, "place_order", {**order, "reduceOnly": True, "closeOnTrigger": True}, native)
            payload = json.loads(received.get(timeout=2)["body"])
            assert payload["qty"] == "0" and payload["reduceOnly"] and payload["closeOnTrigger"]
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
