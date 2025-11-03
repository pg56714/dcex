import pytest
import pytest_asyncio
from dcex.async_support.bingx.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


@pytest.mark.asyncio
async def test_get_swap_instrument_info(client):
    res = await client.get_swap_instrument_info()
    assert res is not None

@pytest.mark.asyncio
async def test_get_orderbook(client):
    res = await client.get_orderbook("BTC-USDT-SWAP", limit=10)
    assert res is not None

@pytest.mark.asyncio
async def test_get_public_trades(client):
    res = await client.get_public_trades("BTC-USDT-SWAP", limit=5)
    assert res is not None

@pytest.mark.asyncio
async def test_get_kline(client):
    res = await client.get_kline("BTC-USDT-SWAP", "1h", limit=5)
    assert res is not None
    
@pytest.mark.asyncio
async def test_get_ticker(client):
    res = await client.get_ticker("BTC-USDT-SWAP")
    assert res is not None
