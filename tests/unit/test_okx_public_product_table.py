"""Public OKX requests must retain table-based FUTURES/OPTION resolution."""

import importlib
import inspect
from urllib.parse import parse_qs, urlsplit

import pytest

from dcex import _native
from tests.unit.native_http_helpers import _http_server

CASES = [
    ("get_orderbook", {}),
    ("get_public_trades", {}),
    ("get_candles_ticks", {}),
    ("get_public_instruments", {"instType": "FUTURES"}),
    ("get_funding_rate", {}),
    ("get_funding_rate_history", {}),
]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "kind,native_symbol", [("FUTURES", "BTC-USD-260327"), ("OPTION", "BTC-USD-260327-80000-C")]
)
@pytest.mark.parametrize("method,extra", CASES)
@pytest.mark.parametrize("loaded", [False, True])
@pytest.mark.asyncio
async def test_public_instrument_query_resolves_loaded_table(
    asynchronous, kind, native_symbol, method, extra, loaded
):
    module = importlib.import_module(
        "dcex." + ("async_support." if asynchronous else "") + "okx.client"
    )
    canonical = native_symbol + "-" + kind
    with _http_server({"code": "0", "data": []}) as (base_url, received):
        client = module.Client(base_api=base_url, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            if loaded:
                client._native_client.set_product_table(
                    _native.ProductTable(
                        [
                            {
                                "exchange": "okx",
                                "product_symbol": canonical,
                                "exchange_symbol": native_symbol,
                                "product_type": kind.lower(),
                                "exchange_type": kind,
                                "base_currency": "BTC",
                                "quote_currency": "USD",
                                "price_precision": "0.1",
                                "size_precision": "1",
                                "min_size": "1",
                                "min_notional": "0",
                                "size_per_contract": "1",
                            }
                        ]
                    )
                )

            async def call():
                kwargs = dict(extra, product_symbol=canonical)
                if "instType" in kwargs:
                    kwargs["instType"] = kind
                value = getattr(client, method)(**kwargs)
                return await value if inspect.isawaitable(value) else value

            if loaded:
                await call()
                assert parse_qs(urlsplit(received.get_nowait()["path"]).query)["instId"] == [
                    native_symbol
                ]
            else:
                with pytest.raises(Exception, match="cannot safely resolve OKX instrument"):
                    await call()
                assert received.empty()
        finally:
            closed = client.close()
            if inspect.isawaitable(closed):
                await closed
