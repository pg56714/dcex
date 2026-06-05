# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.kucoin.client import Client

load_dotenv()

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=KUCOIN_API_KEY,
        api_secret=KUCOIN_API_SECRET,
        passphrase=KUCOIN_API_PASSPHRASE,
    ) as client_instance:
        yield client_instance


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_open_orders(client):
    res = await client.get_spot_open_orders(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_trade_history(client):
    res = await client.get_spot_trade_history(product_symbol="BTC-USDT-SPOT", limit=10)
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_futures_order_list(client):
    res = await client.get_futures_order_list(
        product_symbol="BTC-USDT-SWAP",
        status="active",
        pageSize=10,
    )
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_futures_open_order_value(client):
    res = await client.get_futures_open_order_value(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_futures_trade_history(client):
    res = await client.get_futures_trade_history(product_symbol="BTC-USDT-SWAP", pageSize=10)
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_futures_recent_trade_history(client):
    res = await client.get_futures_recent_trade_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None
