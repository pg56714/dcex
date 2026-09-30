"""Array input representations preserve the documented HTTP payload."""
import importlib
import inspect
import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_backpack_endpoint_coverage import _client_kwargs as backpack_config
from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs as kucoin_config

CASES = json.loads((Path(__file__).parents[1] / "fixtures/array_input_formats.json").read_text(encoding="utf8"))


def config(exchange, base):
    if exchange in {"binance", "bybit"}:
        return dict(api_key="api-key", api_secret="api-secret", preload_product_table=False)
    if exchange == "hyperliquid":
        return dict(wallet_address="0x" + "22" * 20, private_key="0x" + "01" * 32, preload_product_table=False)
    if exchange == "lighter":
        return dict(base_url=base, account_index=12, preload_product_table=False)
    module = importlib.import_module(f"tests.unit.test_{exchange}_endpoint_coverage")
    return module._client_kwargs(base, base) if exchange == "kucoin" else module._client_kwargs(base)


def array_value(request, field):
    query = parse_qs(urlsplit(request["path"]).query)
    try:
        body = json.loads(request["body"])
    except json.JSONDecodeError:
        body = parse_qs(request["body"])
    if field == "$":
        return body
    if isinstance(body, dict) and "action" in body:
        body = body["action"]
    if field == "cancelInfoList":
        params = {**query, **body}
        return [{"orderId": params[f"cancelInfoList[{index}].orderId"][0]} for index in range(sum(key.endswith(".orderId") for key in params))]
    assert isinstance(body, dict) and field in body or field in query, (field, body, query)
    value = body[field] if isinstance(body, dict) and field in body else query[field]
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
        raw = value[0]
        if raw.startswith("["):
            return json.loads(raw)
        if "," in raw:
            return raw.split(",")
    return value


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("case", CASES, ids=lambda c: "/".join(c[k] for k in ("exchange", "method", "field")))
async def test_each_declared_array_has_equivalent_list_and_string_wire(case, asynchronous, monkeypatch):
    exchange = case["exchange"]
    if exchange == "arcus":
        monkeypatch.delenv("ARCUS_API_KEY", raising=False)
        monkeypatch.delenv("ARCUS_API_SIGNING_KEY", raising=False)
        monkeypatch.delenv("ARCUS_ADDRESS", raising=False)
    from dcex import _native
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    response = {"ok": True}
    if exchange == "arcus":
        from tests.unit.test_arcus_endpoint_coverage import MARKETS
        response = MARKETS
    elif exchange == "binance":
        response = {"serverTime": 1700000000000, "data": []}
    elif exchange == "bitget":
        response = {"code": "00000", "data": {}}
    elif exchange == "bybit":
        response = {"retCode": 0, "result": {}}
    elif exchange == "kucoin":
        response = {"code": "200000", "data": {}}
    elif exchange == "okx":
        response = {"code": "0", "data": []}
    elif exchange == "kraken":
        response = {"error": [], "result": {}}
    if exchange == "binance" and case["method"].startswith("cancel_"):
        response = [{"orderId": 1}, {"orderId": 2}]
    with _http_server(response) as (base, received):
        client = cls(**config(exchange, base))
        try:
            if asynchronous:
                await client.async_init()
            if exchange == "binance":
                client._native_client = _native.BinanceHttpClient(api_key="api-key", api_secret="api-secret", timeout=10, spot_base_url=base, futures_base_url=base, coin_futures_base_url=base, options_base_url=base)
            elif exchange == "bybit":
                from tests.unit.test_bybit_endpoint_coverage import _native_client
                client._native_client = _native_client(base)
            elif exchange == "hyperliquid":
                client._native_client = _native.HyperliquidHttpClient(wallet_address="0x" + "22" * 20, private_key="0x" + "01" * 32, timeout=10, endpoint=base)
            results = []
            values = case["values"]
            encoded = ",".join(map(str, values)) if case["representation"] == "csv" else json.dumps(values)
            for value in [values, encoded]:
                kwargs = deepcopy(case["kwargs"])
                kwargs[case["argument"]] = value
                result = getattr(client, case["method"])(**kwargs)
                if inspect.isawaitable(result):
                    await result
                requests = []
                while not received.empty():
                    requests.append(received.get_nowait())
                assert requests
                payload = array_value(requests[-1], case["wire_field"])
                # Arcus signs each cancellation with a fresh timestamp.
                if exchange == "arcus":
                    payload = [{k: v for k, v in item.items() if k not in {"signature", "timestamp"}} for item in payload]
                assert isinstance(payload, list) and len(payload) == len(values), payload
                if exchange == "arcus":
                    assert [item["orderId"] for item in payload] == [item["order_id"] for item in values]
                    assert all(item["marketId"] == 7 for item in payload)
                else:
                    expected = [str(v) for v in values] if case["representation"] in {"csv", "repeated"} else values
                    assert payload == case.get("wire_values", expected), (case, payload)
                if exchange == "kraken" and case["method"] == "get_futures_order_status":
                    raw = parse_qs(urlsplit(requests[-1]["path"]).query or requests[-1]["body"])
                    assert raw[case["wire_field"]] == values
                if exchange == "binance" and case["method"] == "wallet_dust_transfer":
                    raw = parse_qs(urlsplit(requests[-1]["path"]).query or requests[-1]["body"])
                    assert raw["asset"] == [",".join(values)]
                results.append(payload)
            assert results[0] == results[1]
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("encoded", [False, True])
@pytest.mark.parametrize("exchange", ["backpack", "kucoin"])
async def test_array_and_json_string_preserve_documented_wire_shape(exchange, encoded, asynchronous):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    response = {} if exchange == "backpack" else {"code": "200000", "data": {}}
    with _http_server(response) as (base, received):
        client = cls(**(backpack_config(base) if exchange == "backpack" else kucoin_config(base, base)))
        try:
            if asynchronous:
                await client.async_init()
            values = ["SPOT", "PERP"] if exchange == "backpack" else ["XBTUSDTM", "ETHUSDTM"]
            value = json.dumps(values) if encoded else values
            result = client.get_order_history(marketType=value) if exchange == "backpack" else client.set_futures_batch_margin_mode(margin_mode="ISOLATED", symbols=value)
            if inspect.isawaitable(result):
                await result
            request = received.get(timeout=10)
            if exchange == "backpack":
                assert parse_qs(urlsplit(request["path"]).query)["marketType"] == values
            else:
                assert json.loads(request["body"])["symbols"] == values
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


def test_array_format_fixture_covers_all_sixty_seven_declarations():
    from dcex._input_codec import CATALOG
    assert len(CASES) == len({(c['exchange'], c['method'], c['field']) for c in CASES}) == 67
    for case in CASES:
        field = CATALOG['exchanges'][case['exchange']][case['method']]['properties'][case['field']]
        assert field['type'] == 'array'
        assert case['official_source'].startswith('https://')
        if case['representation'] == 'csv':
            assert field.get('x-delimited-string'), case
