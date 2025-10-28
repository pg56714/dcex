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
async def test_get_public_instruments(client):
    res = await client.get_public_instruments(instType="SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_funding_rate(client):
    res = await client.get_funding_rate(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_funding_rate_history(client):
    res = await client.get_funding_rate_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None
