"""Exercise lossless schema inputs at every Python exchange boundary."""

import importlib
import json
from decimal import Decimal

import pytest

from dcex._input_codec import CATALOG
from dcex._input_validation import normalize_endpoint
from dcex._schema_codec import encode_json, normalize

EXCHANGES = [
    "arcus",
    "aster",
    "backpack",
    "binance",
    "bingx",
    "bitget",
    "bybit",
    "extended",
    "hyperliquid",
    "kraken",
    "kucoin",
    "lighter",
    "mexc",
    "okx",
    "ondo",
]


def encoder(exchange, asynchronous):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    if exchange == "arcus":
        return importlib.import_module(f"{prefix}.arcus.client")._params
    if exchange == "binance":
        return importlib.import_module(f"{prefix}.binance._trade_http").TradeHTTP._params
    module = importlib.import_module(f"{prefix}.{exchange}._http_manager")
    if exchange == "ondo":
        return module._params
    return module.HTTPManager._native_params


@pytest.mark.parametrize("exchange", EXCHANGES)
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("value", [1e-7, 0.1 + 0.2, "1e-7", "-3", "abc", "NaN", True])
def test_every_exchange_rejects_lossy_financial_inputs(exchange, asynchronous, value):
    # Use a declared endpoint field; low-level serialization has no context.
    method, key = next((method, key) for method, schema in CATALOG["exchanges"][exchange].items()
                      for key, field in schema["properties"].items()
                      if field.get("format") == "decimal" and not field.get("x-relative") and not field.get("x-signed"))
    with pytest.raises(ValueError, match="decimal"):
        normalize_endpoint(exchange, method, {key: value})


@pytest.mark.parametrize("exchange", EXCHANGES)
@pytest.mark.parametrize("asynchronous", [False, True])
def test_every_exchange_preserves_decimal_precision(exchange, asynchronous):
    text = "0." + "0" * 400 + "123456789012345678901234567890"
    encode = encoder(exchange, asynchronous)
    assert encode(amount=Decimal(text)) == [("amount", text)]
    assert encode(amount=text) == [("amount", text)]


@pytest.mark.parametrize(
    "field",
    [
        "submittedQuantity",
        "submitted_price",
        "qty",
        "price",
        "amount",
        "min_price",
        "total_investment",
        "newPrice",
        "entryPrice",
    ],
)
@pytest.mark.parametrize("value", [0.01, "1e-5", "abc"])
def test_nested_rest_and_ws_inputs_reject_invalid_numbers(field, value):
    with pytest.raises(ValueError):
        normalize({"args": [{field: value}]}, schema={"properties": {"args": {"items": {"properties": {field: {"format": "decimal"}}}}}})


def test_nested_decimal_and_type_encoding():
    assert json.loads(
        encode_json(
            {"args": [{"price": Decimal("0.0000001"), "qty": "2", "reduceOnly": True, "id": -1}]}
        )
    ) == {"args": [{"price": "0.0000001", "qty": "2", "reduceOnly": True, "id": -1}]}
    assert normalize({"priceType": "MARKET", "orderId": "1e-5"}) == {
        "priceType": "MARKET",
        "orderId": "1e-5",
    }


def test_field_names_do_not_determine_validation_policy():
    assert normalize({"price": "label", "amount": -3}) == {"price": "label", "amount": -3}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exchange,class_name,method,args",
    [
        ("kucoin", "ProClient", "send_operation", ("id", "uta.order")),
        ("bybit", "PrivateClient", "send_trade_order", ("order.create",)),
        ("kraken", "V1Client", "send_message", ()),
    ],
)
@pytest.mark.parametrize("price", [0.1 + 0.2, "1e-7", "-3", "abc"])
async def test_ws_numeric_errors_precede_native_send(exchange, class_name, method, args, price):
    from unittest.mock import AsyncMock

    cls = getattr(importlib.import_module(f"dcex.ws.{exchange}"), class_name)
    client = object.__new__(cls)
    client._native_client = AsyncMock()
    with pytest.raises(ValueError, match="decimal"):
        await getattr(client, method)(*args, {"event": "addOrder", "volume": price, "qty": price})
    getattr(client._native_client, method).assert_not_called()


def test_documented_signed_delta_and_market_selector_survive_boundary():
    assert normalize_endpoint("arcus", "adjust_isolated_margin", {"amount": "-5"}) == {"amount": "-5"}
    assert normalize_endpoint("okx", "place_algo_order", {"slOrdPx": "-1"}) == {"slOrdPx": "-1"}
    with pytest.raises(ValueError):
        normalize_endpoint("okx", "place_algo_order", {"slOrdPx": "-2"})


def test_signed_payloads_preserve_decimals_without_accepting_floats():
    assert json.loads(encode_json({"size": Decimal("-1.25")}, signed_fields=("size",))) == {
        "size": "-1.25"
    }
    with pytest.raises(ValueError, match="float"):
        normalize_endpoint("arcus", "adjust_isolated_margin", {"amount": -1.25})
