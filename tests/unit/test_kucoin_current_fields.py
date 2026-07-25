"""Regression coverage for the current KuCoin REST parameter surface."""

# ruff: noqa: D103

from __future__ import annotations

import inspect
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)
from tests.unit.native_http_helpers import _http_server

CURRENT_FIELDS = {
    "get_spot_instrument_info": {"market"},
    "get_futures_orderbook": {"product_symbol", "depth"},
    "get_futures_open_interest": {
        "product_symbol",
        "interval",
        "startAt",
        "endAt",
        "pageSize",
    },
    "get_uta_position_tiers": {
        "product_symbol",
        "tradeType",
        "currency",
        "marginMode",
        "data",
        "accountType",
    },
    "get_uta_fee_rates": {"tradeType", "symbol"},
    "flex_transfer": {
        "fromUserId",
        "toUserId",
        "fromAccountTag",
        "toAccountTag",
        "transfer_type",
    },
    "get_spot_open_orders": {"product_symbol", "pageNum", "pageSize"},
    "get_spot_trade_history": {
        "product_symbol",
        "orderId",
        "side",
        "type_",
        "lastId",
        "startAt",
        "endAt",
        "limit",
    },
    "place_futures_order": {
        "qty",
        "valueQty",
        "forceHold",
        "marginMode",
        "positionSide",
        "stop",
        "stopPriceType",
        "stopPrice",
    },
    "cancel_futures_order_by_client_oid": {"clientOid", "product_symbol"},
    "cancel_futures_all_orders": {"product_symbol"},
    "get_futures_open_order_value": {"product_symbol"},
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_kucoin_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "kucoin")
    async_client = _client_class("async", "kucoin")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


def test_kucoin_removed_obsolete_futures_order_fields() -> None:
    fields = set(
        inspect.signature(_client_class("sync", "kucoin").place_futures_order).parameters
    )

    assert "tags" not in fields


def test_sync_kucoin_forwards_current_public_and_private_fields() -> None:
    client = _client_class("sync", "kucoin")(**_client_kwargs("kucoin"))
    calls = _wire_sync(client)

    client.get_spot_instrument_info(market="USDS")
    client.get_futures_open_interest(
        ["BTC-USDT-SWAP", "ETH-USDT-SWAP"],
    )
    client.get_uta_position_tiers(
        product_symbol="BTC-USDT-SWAP",
        tradeType="FUTURES",
        marginMode="CROSS",
        data="RISK_LIMIT",
        accountType="UNIFIED",
    )
    client.flex_transfer(
        currency="USDT",
        amount="1",
        fromAccountType="ISOLATED",
        fromAccountTag="BTC-USDT",
        toAccountType="TRADE",
    )
    client.get_spot_trade_history(
        "BTC-USDT-SPOT",
        side="buy",
        type_="limit",
        lastId=10,
        limit=100,
    )
    client.place_futures_order(
        "BTC-USDT-SWAP",
        side="buy",
        type_="limit",
        qty="0.001",
        price="100000",
        forceHold=True,
    )

    assert dict(calls[0]["query"]) == {"market": "USDS"}
    assert dict(calls[1]["query"])["product_symbol"] == json.dumps(
        ["BTC-USDT-SWAP", "ETH-USDT-SWAP"], separators=(",", ":")
    )
    assert dict(calls[2]["query"])["data"] == "RISK_LIMIT"
    assert dict(calls[3]["query"])["fromAccountTag"] == "BTC-USDT"
    assert dict(calls[4]["query"])["lastId"] == "10"
    assert dict(calls[4]["query"])["type"] == "limit"
    assert dict(calls[5]["query"])["qty"] == "0.001"
    assert dict(calls[5]["query"])["forceHold"] == "true"


@pytest.mark.asyncio
async def test_async_kucoin_forwards_current_required_fields() -> None:
    client = _client_class("async", "kucoin")(**_client_kwargs("kucoin"))
    calls = _wire_async(client)

    await client.get_uta_fee_rates("FUTURES", "XBTUSDTM")
    await client.cancel_futures_order_by_client_oid(
        "client-1",
        "BTC-USDT-SWAP",
    )
    await client.cancel_futures_all_orders("BTC-USDT-SWAP")
    await client.get_futures_open_order_value("BTC-USDT-SWAP")

    assert dict(calls[0]["query"]) == {"tradeType": "FUTURES", "symbol": "XBTUSDTM"}
    assert dict(calls[1]["query"])["product_symbol"] == "BTC-USDT-SWAP"
    assert dict(calls[2]["query"])["product_symbol"] == "BTC-USDT-SWAP"
    assert dict(calls[3]["query"])["product_symbol"] == "BTC-USDT-SWAP"


def _native_client(base_url: str) -> object:
    native = pytest.importorskip("dcex._native")
    return native.KucoinHttpClient(
        api_key="api-key",
        api_secret="secret",
        passphrase="passphrase",
        timeout=2,
        spot_base_url=base_url,
        futures_base_url=base_url,
    )


def test_native_kucoin_futures_kline_uses_minute_granularity() -> None:
    with _http_server({"code": "200000", "data": []}) as (base_url, received):
        client = _native_client(base_url)
        client.public_request_json(
            "get_futures_kline",
            [
                ("product_symbol", "BTC-USDT-SWAP"),
                ("timeframe", "1m"),
            ],
        )

    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    assert urlsplit(request["path"]).path == "/api/v1/kline/query"
    assert query == {"symbol": "XBTUSDTM", "granularity": "1"}


@pytest.mark.parametrize(
    ("method_name", "params", "message"),
    [
        ("get_spot_open_orders", [], "product_symbol or symbol"),
        (
            "cancel_futures_order_by_client_oid",
            [("clientOid", "client-1")],
            "product_symbol or symbol",
        ),
        ("cancel_futures_all_orders", [], "product_symbol or symbol"),
        ("get_futures_open_order_value", [], "product_symbol or symbol"),
        (
            "place_futures_market_order",
            [
                ("product_symbol", "BTC-USDT-SWAP"),
                ("side", "buy"),
                ("size", "1"),
                ("qty", "0.001"),
            ],
            "exactly one of size, qty, valueQty",
        ),
        (
            "flex_transfer",
            [
                ("transfer_type", "PARENT_TO_SUB"),
                ("currency", "USDT"),
                ("amount", "1"),
                ("fromAccountType", "MARGIN_V2"),
                ("toAccountType", "TRADE"),
                ("toUserId", "sub-user"),
            ],
            "cannot use a V2 margin account type",
        ),
    ],
)
def test_native_kucoin_rejects_invalid_current_parameters_before_transport(
    method_name: str,
    params: list[tuple[str, str]],
    message: str,
) -> None:
    client = _native_client("http://127.0.0.1:1")

    with pytest.raises(ValueError, match=message):
        client.private_request_json(method_name, params)
