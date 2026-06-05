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
@pytest.mark.private
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


@pytest.mark.asyncio
async def test_get_futures_contracts(client):
    res = await client.get_futures_contracts()
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_contract(client):
    res = await client.get_futures_contract(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_ticker(client):
    res = await client.get_futures_ticker(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_orderbook(client):
    res = await client.get_futures_orderbook(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_part_orderbook(client):
    res = await client.get_futures_orderbook(product_symbol="BTC-USDT-SWAP", depth=20)
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_public_trades(client):
    res = await client.get_futures_public_trades(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_kline(client):
    res = await client.get_futures_kline(product_symbol="BTC-USDT-SWAP", timeframe="1m")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_open_interest(client):
    res = await client.get_futures_open_interest(product_symbol="BTC-USDT-SWAP")
    assert res is not None
