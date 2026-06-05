# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bingx.client import Client

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
async def test_get_swap_open_orders(client):
    res = await client.get_open_orders(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_swap_order_history(client):
    res = await client.get_order_history(product_symbol="BTC-USDT-SWAP", limit=5)
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_margin_type(client):
    res = await client.get_margin_type(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_leverage(client):
    res = await client.get_leverage(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_position_mode(client):
    res = await client.get_position_mode()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_test_swap_order(client):
    res = await client.test_swap_order(
        product_symbol="BTC-USDT-SWAP",
        type_="LIMIT",
        side="BUY",
        positionSide="LONG",
        quantity=0.0001,
        price=30000,
        timeInForce="GTC",
    )
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_open_orders(client):
    res = await client.get_spot_open_orders(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_order_history(client):
    res = await client.get_spot_order_history(product_symbol="BTC-USDT-SPOT", pageSize=5)
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_my_trades(client):
    res = await client.get_spot_my_trades(product_symbol="BTC-USDT-SPOT", limit=5)
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_commission_rate(client):
    res = await client.get_spot_commission_rate(product_symbol="BTC-USDT-SPOT")
    assert res is not None
