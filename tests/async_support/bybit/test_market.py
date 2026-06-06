# ruff: noqa: ANN001, ANN201, D100, D103

import pytest
import pytest_asyncio

from dcex.async_support.bybit.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


@pytest.mark.asyncio
async def test_get_instruments_info(client):
    res = await client.get_instruments_info(category="spot")
    assert res is not None


@pytest.mark.asyncio
async def test_get_kline(client):
    res = await client.get_kline(
        product_symbol="BTC-USDT-SPOT",
        interval="1m",
    )
    assert res is not None


@pytest.mark.asyncio
async def test_get_orderbook(client):
    res = await client.get_orderbook(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_tickers(client):
    res = await client.get_tickers()
    assert res is not None


@pytest.mark.asyncio
async def test_get_funding_rate_history(client):
    res = await client.get_funding_rate_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_public_trade_history(client):
    res = await client.get_public_trade_history(product_symbol="BTC-USDT-SPOT", limit=10)
    assert res is not None


@pytest.mark.asyncio
async def test_get_open_interest(client):
    res = await client.get_open_interest(product_symbol="BTC-USDT-SWAP", limit=10)
    assert res is not None


@pytest.mark.asyncio
async def test_get_long_short_ratio(client):
    res = await client.get_long_short_ratio(product_symbol="BTC-USDT-SWAP", limit=10)
    assert res is not None


@pytest.mark.asyncio
async def test_get_historical_volatility(client):
    res = await client.get_historical_volatility(baseCoin="BTC", period=7)
    assert res is not None


@pytest.mark.asyncio
async def test_get_insurance_pool(client):
    res = await client.get_insurance_pool(coin="USDT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_delivery_price(client):
    res = await client.get_delivery_price(category="linear", baseCoin="BTC", limit=10)
    assert res is not None


@pytest.mark.asyncio
async def test_get_order_price_limit(client):
    res = await client.get_order_price_limit(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_adl_alert(client):
    res = await client.get_adl_alert(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_risk_limit(client):
    res = await client.get_risk_limit(product_symbol="BTC-USDT-SWAP")
    assert res is not None
