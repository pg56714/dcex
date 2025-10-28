import pytest
import pytest_asyncio
from dcex.async_support.okx.client import Client


@pytest_asyncio.fixture
async def client():
    import asyncio

    client_instance = Client()
    await client_instance.async_init()
    yield client_instance
    await client_instance.close()
    await asyncio.sleep(0.05)


@pytest.mark.asyncio
async def test_get_candles_ticks(client):
    res = await client.get_candles_ticks(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_orderbook(client):
    res = await client.get_orderbook(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_tickers(client):
    res = await client.get_tickers(instType="SPOT")
    assert res is not None

@pytest.mark.asyncio
async def test_get_public_trades(client):
    res = await client.get_public_trades(product_symbol="BTC-USDT-SPOT")
    assert res is not None
