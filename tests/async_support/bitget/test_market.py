# ruff: noqa: ANN001, ANN201, D100, D103

import pytest
import pytest_asyncio

from dcex.async_support.bitget.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


def _assert_success(res) -> None:
    assert res["code"] == "00000"
    assert "data" in res


@pytest.mark.asyncio
async def test_get_spot_coins(client):
    res = await client.get_spot_coins(coin="USDT")
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_spot_market_trades(client):
    res = await client.get_spot_market_trades(product_symbol="BTC-USDT-SPOT", limit=5)
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "category,symbol", [("SPOT", "BTC-USDT-SPOT"), ("USDT-FUTURES", "BTC-USDT-SWAP")]
)
async def test_uta_market_data(client, category, symbol):
    _assert_success(await client.get_uta_instruments(category, product_symbol=symbol))
    _assert_success(await client.get_uta_tickers(category, product_symbol=symbol))
    book = await client.get_uta_orderbook(category, symbol, limit=5)
    _assert_success(book)
    assert book["data"]["bids"] and book["data"]["asks"]
