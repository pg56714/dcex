"""BingX coin-M attached prices retain exact fractional JSON-number values."""

from decimal import Decimal
import importlib
import inspect
import json
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_bingx_endpoint_coverage import _client_kwargs


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_coin_swap_tpsl_exact_number_wire(asynchronous):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.bingx.client").Client
    with _http_server({"code": 0, "data": {}}) as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            response = client.place_coin_swap_order(
                product_symbol="BTC-USD-SWAP", side="BUY", type_="MARKET", quantity="1",
                take_profit={"type": "TAKE_PROFIT", "stopPrice": "61000.5", "price": Decimal("61000.125000000000000001")},
                stop_loss={"type": "STOP_MARKET", "stopPrice": Decimal("59000.75")},
            )
            if inspect.isawaitable(response):
                await response
            request = received.get_nowait()
            assert request["method"] == "POST"
            assert urlsplit(request["path"]).path == "/openApi/cswap/v1/trade/order"
            params = parse_qs(urlsplit(request["path"]).query or request["body"])
            tp = json.loads(params["takeProfit"][0], parse_float=Decimal)
            sl = json.loads(params["stopLoss"][0], parse_float=Decimal)
            assert tp["stopPrice"] == Decimal("61000.5")
            assert tp["price"] == Decimal("61000.125000000000000001")
            assert sl["stopPrice"] == Decimal("59000.75")
        finally:
            closed = client.close()
            if inspect.isawaitable(closed):
                await closed
