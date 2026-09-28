"""Offline coverage for kucoin order validation."""
# ruff: noqa: ANN001, ANN201, D103

from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_binance_batch_orders import invoke


@pytest.mark.parametrize(
    "trade_type,symbol,expected",
    [("MARGIN", "BTC-USDT-SPOT", "BTC-USDT"), ("FUTURES", "BTC-USDT-SWAP", "XBTUSDTM")],
)
def test_kucoin_leverage_uses_requested_market(trade_type, symbol, expected):
    from dcex.kucoin.client import Client
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs

    with _http_server({"code": "200000", "data": {}}) as (base, received):
        client = Client(**_client_kwargs(base, base))
        try:
            client.get_uta_leverage(trade_type, product_symbol=symbol)
        finally:
            client.close()
        assert (
            dict(parse_qsl(urlsplit(received.get(timeout=2)["path"]).query))["symbol"] == expected
        )


def test_kucoin_stop_order_generates_client_id():
    from dcex.kucoin.client import Client
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs

    with _http_server({"code": "200000", "data": {}}) as (base, received):
        client = Client(**_client_kwargs(base, base))
        try:
            client.place_spot_stop_order(
                "buy", "BTC-USDT-SPOT", "limit", "90", price="100", size="1"
            )
        finally:
            client.close()
        body = json.loads(received.get(timeout=2)["body"])
        assert isinstance(body["clientOid"], str) and len(body["clientOid"]) > 10


def test_kucoin_batch_cancel_rejects_both_identifier_lists():
    from dcex.kucoin.client import Client
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs

    with _http_server({"code": "200000", "data": {}}) as (base, received):
        client = Client(**_client_kwargs(base, base))
        try:
            with pytest.raises(ValueError):
                client.cancel_futures_batch_orders(
                    order_ids=["1"], client_orders=[{"symbol": "XBTUSDTM", "clientOid": "mine"}]
                )
        finally:
            client.close()
        assert received.empty()


import inspect
import json

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "trade_type,symbol", [("MARGIN", "BTC-USDT-SWAP"), ("FUTURES", "BTC-USDT-SPOT")]
)
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
                await invoke(
                    client, "get_uta_leverage", trade_type=trade_type, product_symbol=symbol
                )
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        assert received.empty()
