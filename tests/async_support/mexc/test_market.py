# ruff: noqa: ANN001, ANN201, D100, D103

import pytest
import pytest_asyncio

from dcex.async_support.mexc.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


def _assert_contract_success(res) -> None:
    assert res["success"] is True
    assert res["code"] == 0
    assert "data" in res


@pytest.mark.asyncio
async def test_ping(client):
    res = await client.ping()
    assert isinstance(res, dict)


@pytest.mark.asyncio
async def test_get_spot_time(client):
    res = await client.get_spot_time()
    assert res["serverTime"] > 0


@pytest.mark.asyncio
async def test_get_spot_default_symbols(client):
    res = await client.get_spot_default_symbols()
    assert "data" in res


@pytest.mark.asyncio
async def test_get_spot_exchange_info(client):
    res = await client.get_spot_exchange_info(product_symbol="BTC-USDT-SPOT")
    assert res["symbols"]
    assert res["symbols"][0]["symbol"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_get_spot_orderbook(client):
    res = await client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", limit=5)
    assert res["bids"]
    assert res["asks"]


@pytest.mark.asyncio
async def test_get_spot_recent_trades(client):
    res = await client.get_spot_recent_trades(product_symbol="BTC-USDT-SPOT", limit=2)
    assert res


@pytest.mark.asyncio
async def test_get_spot_agg_trades(client):
    res = await client.get_spot_agg_trades(product_symbol="BTC-USDT-SPOT", limit=2)
    assert res


@pytest.mark.asyncio
async def test_get_spot_klines(client):
    res = await client.get_spot_klines(product_symbol="BTC-USDT-SPOT", interval="1m", limit=2)
    assert res


@pytest.mark.asyncio
async def test_get_spot_avg_price(client):
    res = await client.get_spot_avg_price(product_symbol="BTC-USDT-SPOT")
    assert float(res["price"]) > 0


@pytest.mark.asyncio
async def test_get_spot_ticker_24hr(client):
    res = await client.get_spot_ticker_24hr(product_symbol="BTC-USDT-SPOT")
    assert res["symbol"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_get_spot_ticker_price(client):
    res = await client.get_spot_ticker_price(product_symbol="BTC-USDT-SPOT")
    assert res["symbol"] == "BTCUSDT"
    assert float(res["price"]) > 0


@pytest.mark.asyncio
async def test_get_spot_book_ticker(client):
    res = await client.get_spot_book_ticker(product_symbol="BTC-USDT-SPOT")
    assert res["symbol"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_get_contract_time(client):
    res = await client.get_contract_time()
    _assert_contract_success(res)
    assert res["data"] > 0


@pytest.mark.asyncio
async def test_get_contract_details(client):
    res = await client.get_contract_details(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


@pytest.mark.asyncio
async def test_get_contract_ticker(client):
    res = await client.get_contract_ticker(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


@pytest.mark.asyncio
async def test_get_contract_depth(client):
    res = await client.get_contract_depth(product_symbol="BTC-USDT-SWAP", limit=5)
    _assert_contract_success(res)
    assert res["data"]["bids"]
    assert res["data"]["asks"]


@pytest.mark.asyncio
async def test_get_contract_depth_commits(client):
    res = await client.get_contract_depth_commits(product_symbol="BTC-USDT-SWAP", limit=5)
    _assert_contract_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_contract_index_price(client):
    res = await client.get_contract_index_price(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


@pytest.mark.asyncio
async def test_get_contract_fair_price(client):
    res = await client.get_contract_fair_price(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


@pytest.mark.asyncio
async def test_get_contract_funding_rate(client):
    res = await client.get_contract_funding_rate(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


@pytest.mark.asyncio
async def test_get_contract_kline(client):
    res = await client.get_contract_kline(product_symbol="BTC-USDT-SWAP", interval="Min1")
    _assert_contract_success(res)
    assert res["data"]["time"]


@pytest.mark.asyncio
async def test_get_contract_index_price_kline(client):
    res = await client.get_contract_index_price_kline(
        product_symbol="BTC-USDT-SWAP",
        interval="Min1",
    )
    _assert_contract_success(res)
    assert res["data"]["time"]


@pytest.mark.asyncio
async def test_get_contract_fair_price_kline(client):
    res = await client.get_contract_fair_price_kline(
        product_symbol="BTC-USDT-SWAP",
        interval="Min1",
    )
    _assert_contract_success(res)
    assert res["data"]["time"]


@pytest.mark.asyncio
async def test_get_contract_deals(client):
    res = await client.get_contract_deals(product_symbol="BTC-USDT-SWAP", limit=2)
    _assert_contract_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_contract_risk_reverse(client):
    res = await client.get_contract_risk_reverse(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]


@pytest.mark.asyncio
async def test_get_contract_risk_reverse_history(client):
    res = await client.get_contract_risk_reverse_history(
        product_symbol="BTC-USDT-SWAP",
        page_num=1,
        page_size=2,
    )
    _assert_contract_success(res)
    assert res["data"]["resultList"]


@pytest.mark.asyncio
async def test_get_contract_funding_rate_history(client):
    res = await client.get_contract_funding_rate_history(
        product_symbol="BTC-USDT-SWAP",
        page_num=1,
        page_size=2,
    )
    _assert_contract_success(res)
    assert res["data"]["resultList"]
