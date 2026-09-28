"""Kraken relative prices survive native REST and V1 WS transport."""

import asyncio
import importlib
import inspect
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.test_kraken_endpoint_coverage import _client_kwargs, _route_server
from tests.unit.ws_test_peer import echo_peer


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("value", ["+5", "-5", "#5", "+5.25%", "-5%", "#5.5%"])
@pytest.mark.parametrize("method,path,kwargs,fields", [
    ("place_spot_order", "/0/private/AddOrder", {"product_symbol":"BTC-USD-SPOT", "side":"buy", "ordertype":"limit", "volume":"1"}, {"price":"price", "price2":"price2", "close_price":"close[price]"}),
    ("amend_spot_order", "/0/private/AmendOrder", {"txid":"order-id"}, {"limit_price":"limit_price", "trigger_price":"trigger_price"}),
    ("edit_spot_order", "/0/private/EditOrder", {"pair":"XBTUSD", "txid":"order-id"}, {"price":"price", "price2":"price2"}),
])
async def test_relative_rest_wire(asynchronous, value, method, path, kwargs, fields):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.kraken.client").Client
    with _route_server() as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            result = getattr(client, method)(**kwargs, **dict.fromkeys(fields, value))
            if inspect.isawaitable(result):
                await result
            request = received.get(timeout=2)
            assert request["method"] == "POST"
            assert urlsplit(request["path"]).path == path
            payload = parse_qs(request["body"])
            for wire in fields.values():
                assert payload[wire] == [value]
        finally:
            closed = client.close()
            if inspect.isawaitable(closed):
                await closed


@pytest.mark.asyncio
@pytest.mark.parametrize("event", ["addOrder", "editOrder", "amendOrder"])
@pytest.mark.parametrize("value", ["+5", "-5", "#5", "+5.25%", "-5%", "#5.5%"])
async def test_relative_ws_wire(event, value):
    from dcex.ws.kraken import V1Client
    payload = {"event":event, "pair":"XBT/USD", "type":"buy", "ordertype":"limit", "volume":"1", "price":value, "price2":value}
    if event == "editOrder":
        payload["orderid"] = "order-id"
    if event == "addOrder":
        payload.update({"close[price]": value, "close[price2]": value})
    if event == "amendOrder":
        payload = {"event": event, "order_id": "order-id", "limit_price": value, "trigger_price": value}
    async with echo_peer() as (url, received):
        client = V1Client("offline-token", base_url=url, timeout=2)
        try:
            await client.connect()
            await client.send_message(payload)
            result = await asyncio.wait_for(client.recv(), 3)
            assert result == {**payload, "token":"offline-token"}
        finally:
            await client.close()
    assert received == [{**payload, "token":"offline-token"}]
