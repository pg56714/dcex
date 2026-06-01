import pytest
import pytest_asyncio
from dcex.async_support.binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()


BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
    ) as client_instance:
        yield client_instance


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_account_balance(client):
    res = await client.get_account_balance(market_type="spot")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_futures_account_balance(client):
    res = await client.get_account_balance(market_type="swap")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_futures_account_info(client):
    res = await client.get_futures_account_info()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_income_history(client):
    res = await client.get_income_history()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_rest_listen_key_is_unavailable(client):
    with pytest.raises(NotImplementedError):
        await client.get_listen_key(market_type="spot")


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_listen_key_lifecycle(client):
    listen_key = await client.get_listen_key(market_type="swap")
    assert listen_key
    assert await client.keep_alive_listen_key(listen_key, market_type="swap") is not None
    assert await client.close_listen_key(listen_key, market_type="swap") is not None
