# ruff: noqa: ANN001, ANN201, D100, D103

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
async def test_get_swap_orderbook(client):
    res = await client.get_orderbook("BTC-USDT-SWAP", limit=10)
    assert res is not None


@pytest.mark.asyncio
async def test_get_swap_public_trades(client):
    res = await client.get_public_trades("BTC-USDT-SWAP", limit=5)
    assert res is not None


@pytest.mark.asyncio
async def test_get_swap_kline(client):
    res = await client.get_kline("BTC-USDT-SWAP", "1h", limit=5)
    assert res is not None


@pytest.mark.asyncio
async def test_get_swap_ticker(client):
    res = await client.get_ticker("BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_swap_open_interest(client):
    res = await client.get_open_interest("BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_swap_mark_price_kline(client):
    res = await client.get_mark_price_kline("BTC-USDT-SWAP", "1h", limit=5)
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_instrument_info(client):
    res = await client.get_spot_instrument_info()
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_orderbook(client):
    res = await client.get_spot_orderbook("BTC-USDT-SPOT", limit=10)
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_orderbook_v2(client):
    res = await client.get_spot_orderbook_v2("BTC-USDT-SPOT", limit=10)
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_public_trades(client):
    res = await client.get_spot_public_trades("BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_kline(client):
    res = await client.get_spot_kline("BTC-USDT-SPOT", "1h", limit=5)
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_kline_v2(client):
    res = await client.get_spot_kline_v2("BTC-USDT-SPOT", "1h", limit=5)
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_ticker(client):
    res = await client.get_spot_ticker("BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_book_ticker(client):
    res = await client.get_spot_book_ticker("BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_price_ticker(client):
    res = await client.get_spot_price_ticker("BTC-USDT-SPOT")
    assert res is not None
