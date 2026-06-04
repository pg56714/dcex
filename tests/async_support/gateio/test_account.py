import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.gateio.client import Client

load_dotenv()


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=os.getenv("GATEIO_API_KEY"),
        api_secret=os.getenv("GATEIO_API_SECRET"),
    ) as client_instance:
        yield client_instance


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_futures_account(client):
    res = await client.get_futures_account()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_total_balance(client):
    res = await client.get_total_balance(currency="USDT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_unified_accounts(client):
    res = await client.get_unified_accounts()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_futures_account_book(client):
    res = await client.get_futures_account_book()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_delivery_account(client):
    res = await client.get_delivery_account()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_delivery_account_book(client):
    res = await client.get_delivery_account_book()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_account(client):
    res = await client.get_spot_account(ccy="btc")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_account_book(client):
    res = await client.get_spot_account_book()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_fee(client):
    res = await client.get_spot_fee(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_batch_fee(client):
    res = await client.get_spot_batch_fee(["BTC-USDT-SPOT", "ETH-USDT-SPOT"])
    assert res is not None
