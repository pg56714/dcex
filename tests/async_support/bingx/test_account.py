import pytest
import pytest_asyncio
from dcex.async_support.bingx.client import Client
import os
from dotenv import load_dotenv

load_dotenv()


BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BINGX_API_KEY,
        api_secret=BINGX_API_SECRET,
    ) as client_instance:
        yield client_instance


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_account_balance(client):
    res = await client.get_account_balance()
    assert res is not None

@pytest.mark.asyncio
@pytest.mark.private
async def test_get_open_positions(client):
    res = await client.get_open_positions(product_symbol="BTC-USDT-SWAP")
    assert res is not None

@pytest.mark.asyncio
@pytest.mark.private
async def test_get_fund_flow(client):
    res = await client.get_fund_flow(limit=5)
    assert res is not None

@pytest.mark.asyncio
@pytest.mark.private
async def test_get_listen_key(client):
    res = await client.get_listen_key()
    assert res is not None
