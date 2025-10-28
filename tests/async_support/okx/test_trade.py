import pytest
import pytest_asyncio
from dcex.async_support.okx.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")


@pytest_asyncio.fixture
async def client():
    import asyncio

    client_instance = Client(
        api_key=OKX_API_KEY,
        api_secret=OKX_API_SECRET,
        passphrase=OKX_PASSPHRASE,
    )
    await client_instance.async_init()
    yield client_instance
    await client_instance.close()
    await asyncio.sleep(0.05)


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_order_list(client):
    res = await client.get_order_list(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_orders_history(client):
    res = await client.get_orders_history(instType="SPOT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_orders_history_archive(client):
    res = await client.get_orders_history_archive(instType="SPOT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_fills(client):
    res = await client.get_fills()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_fills_history(client):
    res = await client.get_fills_history(instType="SPOT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_account_rate_limit(client):
    res = await client.get_account_rate_limit()
    assert res is not None
