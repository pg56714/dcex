# ruff: noqa: ANN001, ANN201, D100, D103

import pytest
import pytest_asyncio

from dcex.async_support.kraken.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


@pytest.mark.asyncio
async def test_get_server_time(client):
    res = await client.get_server_time()
    assert res["result"]["unixtime"] > 0


@pytest.mark.asyncio
async def test_get_spot_asset_pairs(client):
    res = await client.get_spot_asset_pairs(pair="XBTUSDT")
    assert "XBTUSDT" in res["result"]


@pytest.mark.asyncio
async def test_get_spot_ticker(client):
    res = await client.get_spot_ticker(product_symbol="BTC-USDT-SPOT")
    assert res["result"]


@pytest.mark.asyncio
async def test_get_spot_orderbook(client):
    res = await client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", count=5)
    assert res["result"]


@pytest.mark.asyncio
async def test_get_spot_public_trades(client):
    res = await client.get_spot_public_trades(product_symbol="BTC-USDT-SPOT")
    assert res["result"]


@pytest.mark.asyncio
async def test_get_spot_kline(client):
    res = await client.get_spot_kline(product_symbol="BTC-USDT-SPOT", interval=1)
    assert res["result"]


@pytest.mark.asyncio
async def test_get_futures_instruments(client):
    res = await client.get_futures_instruments(contractType="flexible_futures")
    assert res["result"] == "success"
    assert res["instruments"]


@pytest.mark.asyncio
async def test_get_futures_tickers(client):
    res = await client.get_futures_tickers(product_symbol="BTC-USD-SWAP")
    assert res["result"] == "success"
    assert res["tickers"]


@pytest.mark.asyncio
async def test_get_futures_orderbook(client):
    res = await client.get_futures_orderbook(product_symbol="BTC-USD-SWAP")
    assert res["result"] == "success"
    assert res["orderBook"]


@pytest.mark.asyncio
async def test_get_futures_public_trades(client):
    res = await client.get_futures_public_trades(product_symbol="BTC-USD-SWAP")
    assert res["result"] == "success"
    assert res["history"]


@pytest.mark.asyncio
async def test_get_futures_kline(client):
    res = await client.get_futures_kline(
        product_symbol="BTC-USD-SWAP",
        timeframe="1m",
        count=5,
    )
    assert res["candles"]
