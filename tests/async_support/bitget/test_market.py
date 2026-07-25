# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest
import pytest_asyncio

from dcex.async_support.bitget.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


def _assert_success(res) -> None:
    assert res["code"] == "00000"
    assert "data" in res


@pytest.mark.asyncio
async def test_get_spot_coins(client):
    res = await client.get_spot_coins(coin="USDT")
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_spot_symbols(client):
    res = await client.get_spot_symbols(product_symbol="BTC-USDT-SPOT")
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_spot_tickers(client):
    res = await client.get_spot_tickers(product_symbol="BTC-USDT-SPOT")
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_spot_orderbook(client):
    res = await client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", limit=5)
    _assert_success(res)
    assert res["data"]["bids"]
    assert res["data"]["asks"]


@pytest.mark.asyncio
async def test_get_spot_kline(client):
    res = await client.get_spot_kline(
        product_symbol="BTC-USDT-SPOT",
        granularity="1min",
        limit=5,
    )
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_spot_history_kline(client):
    end_time = int(time.time() * 1000)
    res = await client.get_spot_history_kline(
        product_symbol="BTC-USDT-SPOT",
        granularity="1min",
        endTime=end_time,
        limit=5,
    )
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_spot_recent_trades(client):
    res = await client.get_spot_recent_trades(product_symbol="BTC-USDT-SPOT", limit=5)
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_spot_market_trades(client):
    res = await client.get_spot_market_trades(product_symbol="BTC-USDT-SPOT", limit=5)
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_contracts(client):
    res = await client.get_futures_contracts(product_symbol="BTC-USDT-SWAP")
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_ticker(client):
    res = await client.get_futures_ticker(product_symbol="BTC-USDT-SWAP")
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_tickers(client):
    res = await client.get_futures_tickers()
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_orderbook(client):
    res = await client.get_futures_orderbook(product_symbol="BTC-USDT-SWAP", limit=5)
    _assert_success(res)
    assert res["data"]["bids"]
    assert res["data"]["asks"]


@pytest.mark.asyncio
async def test_get_futures_kline(client):
    res = await client.get_futures_kline(
        product_symbol="BTC-USDT-SWAP",
        granularity="1m",
        limit=5,
    )
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_history_kline(client):
    res = await client.get_futures_history_kline(
        product_symbol="BTC-USDT-SWAP",
        granularity="1m",
        limit=5,
    )
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_recent_trades(client):
    res = await client.get_futures_recent_trades(product_symbol="BTC-USDT-SWAP", limit=5)
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_current_funding_rate(client):
    res = await client.get_futures_current_funding_rate(product_symbol="BTC-USDT-SWAP")
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_history_funding_rate(client):
    res = await client.get_futures_history_funding_rate(
        product_symbol="BTC-USDT-SWAP",
        pageSize=5,
    )
    _assert_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_futures_open_interest(client):
    res = await client.get_futures_open_interest(product_symbol="BTC-USDT-SWAP")
    _assert_success(res)
    assert res["data"]
