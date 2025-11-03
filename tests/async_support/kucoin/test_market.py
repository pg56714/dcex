import pytest
import pytest_asyncio
from dcex.async_support.kucoin.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


@pytest.mark.asyncio
async def test_get_spot_instrument_info(client):
    res = await client.get_spot_instrument_info()
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_ticker(client):
    res = await client.get_spot_ticker(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_all_tickers(client):
    res = await client.get_spot_all_tickers()
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_orderbook(client):
    res = await client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_public_trades(client):
    res = await client.get_spot_public_trades(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_kline(client):
    res = await client.get_spot_kline(product_symbol="BTC-USDT-SPOT", timeframe="1m")
    assert res is not None
