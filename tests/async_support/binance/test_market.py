# ruff: noqa: ANN001, ANN201, D100, D103

import pytest
import pytest_asyncio

from dcex.async_support.binance.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


@pytest.mark.asyncio
async def test_get_spot_exchange_info(client):
    res = await client.get_spot_exchange_info(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_orderbook(client):
    res = await client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", limit=5)
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_trades(client):
    res = await client.get_spot_trades(product_symbol="BTC-USDT-SPOT", limit=5)
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_server_time(client):
    res = await client.get_server_time(market_type="spot")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_server_time(client):
    res = await client.get_server_time(market_type="swap")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_exchange_info(client):
    res = await client.get_futures_exchange_info()
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_ticker(client):
    res = await client.get_futures_ticker(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_klines(client):
    res = await client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_premium_index(client):
    res = await client.get_futures_premium_index(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_funding_rate(client):
    res = await client.get_futures_funding_rate(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_open_interest(client):
    res = await client.get_futures_open_interest(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_open_interest_history(client):
    res = await client.get_futures_open_interest_history(
        product_symbol="BTC-USDT-SWAP", period="5m", limit=5
    )
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_global_long_short_account_ratio(client):
    res = await client.get_futures_global_long_short_account_ratio(
        product_symbol="BTC-USDT-SWAP", period="5m", limit=5
    )
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_top_long_short_account_ratio(client):
    res = await client.get_futures_top_long_short_account_ratio(
        product_symbol="BTC-USDT-SWAP", period="5m", limit=5
    )
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_top_long_short_position_ratio(client):
    res = await client.get_futures_top_long_short_position_ratio(
        product_symbol="BTC-USDT-SWAP", period="5m", limit=5
    )
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_taker_buy_sell_volume(client):
    res = await client.get_futures_taker_buy_sell_volume(
        product_symbol="BTC-USDT-SWAP", period="5m", limit=5
    )
    assert res is not None


@pytest.mark.asyncio
async def test_get_futures_basis(client):
    res = await client.get_futures_basis(
        product_symbol="BTC-USDT-SWAP",
        contractType="PERPETUAL",
        period="5m",
        limit=5,
    )
    assert res is not None
