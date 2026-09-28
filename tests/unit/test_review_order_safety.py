"""Regression coverage for reviewed nonce, position-side and market boundaries."""

import importlib
import inspect
import time
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_binance_batch_orders import invoke


@pytest.mark.parametrize("exchange", ["bitmart", "bitmex", "decibel", "gateio"])
@pytest.mark.parametrize("prefix", ["dcex", "dcex.async_support"])
def test_unimplemented_exchanges_are_not_empty_importable_packages(prefix, exchange):
    assert importlib.util.find_spec(f"{prefix}.{exchange}") is None


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.asyncio
async def test_aster_guarded_future_nonce_preserves_automatic_clock(asynchronous):
    from tests.unit.test_aster_endpoint_coverage import _client_kwargs

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.aster.client").Client
    with _http_server() as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            before = client.reserve_nonce()
            await invoke(
                client,
                "guarded_cancel_futures_order",
                product_symbol="BTC-USDT-SWAP",
                orderId=123,
                nonce=before * 1000,
            )
            after = client.reserve_nonce()
            assert before < after < time.time_ns() // 1000 + 60_000_000
            assert received.qsize() == 1
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", ["place_swap_market_sell_order", "place_swap_limit_sell_order"])
def test_bingx_sell_requires_explicit_position_side(asynchronous, method):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.bingx.client").Client
    signature = inspect.signature(getattr(cls, method))
    assert signature.parameters["position_side"].default is inspect.Parameter.empty
    args = {"self": object(), "product_symbol": "BTC-USDT-SWAP", "quantity": "1"}
    if "limit" in method:
        args["price"] = "10"
    with pytest.raises(TypeError, match="position_side"):
        signature.bind(**args)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.asyncio
async def test_bingx_client_order_ids_wire_name(asynchronous):
    from tests.unit.test_bingx_endpoint_coverage import _client_kwargs

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.bingx.client").Client
    with _http_server({"code": 0, "data": {}}) as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            await invoke(
                client,
                "cancel_spot_batch_orders",
                product_symbol="BTC-USDT-SPOT",
                order_ids=[123],
                client_order_ids=["client-1", "client-2"],
            )
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        request = received.get_nowait()
    params = parse_qs(urlsplit(request["path"]).query or request["body"])
    assert params["clientOrderIDs"] == ["client-1,client-2"]
    assert "clientOrderIds" not in params


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "trade_type,symbol",
    [("MARGIN", "BTC-USDT-SWAP"), ("SPOT", "XBTUSDTM"), ("FUTURES", "BTC-USDT-SPOT")],
)
@pytest.mark.asyncio
async def test_kucoin_batch_cancel_rejects_market_mismatch(asynchronous, trade_type, symbol):
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.kucoin.client").Client
    with _http_server() as (base, received):
        client = cls(**_client_kwargs(base, base))
        if asynchronous:
            await client.async_init()
        try:
            with pytest.raises(ValueError, match="tradeType"):
                await invoke(
                    client,
                    "batch_cancel_uta_orders",
                    trade_type=trade_type,
                    cancel_order_list=[{"symbol": symbol, "orderId": "123"}],
                )
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        assert received.empty()
