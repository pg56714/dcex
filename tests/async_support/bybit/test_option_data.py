# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bybit.client import Client

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

GREEK_KEYS = {"markIv", "delta", "gamma", "vega", "theta"}


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


@pytest_asyncio.fixture
async def private_client():
    async with Client(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET) as client_instance:
        yield client_instance


def _assert_ok(response):
    assert response["retCode"] == 0, response
    assert "result" in response
    return response["result"]


async def _active_btc_option(client) -> str:
    result = _assert_ok(await client.get_instruments_info(category="option", baseCoin="BTC"))
    options = [row for row in result["list"] if row["status"] == "Trading"]
    assert options
    return min(options, key=lambda row: int(row["deliveryTime"]))["symbol"]


@pytest.mark.asyncio
async def test_option_market_data_endpoints(client):
    symbol = await _active_btc_option(client)

    tickers = _assert_ok(await client.get_tickers(category="option", baseCoin="BTC"))["list"]
    assert tickers
    assert GREEK_KEYS <= tickers[0].keys()

    ticker = _assert_ok(await client.get_tickers(category="option", product_symbol=symbol))["list"]
    assert [row["symbol"] for row in ticker] == [symbol]
    assert GREEK_KEYS <= ticker[0].keys()

    orderbook = _assert_ok(await client.get_orderbook(product_symbol=symbol, limit=5))
    assert orderbook["s"] == symbol
    assert {"b", "a"} <= orderbook.keys()


@pytest.mark.asyncio
async def test_option_reference_endpoints(client):
    base_coins = _assert_ok(await client.get_option_base_coins())["list"]
    assert any(row["baseCoin"] == "BTC" for row in base_coins)

    deliveries = _assert_ok(
        await client.get_option_delivery_prices(category="option", base_coin="BTC")
    )
    assert deliveries["list"]
    assert {"deliveryPrice", "deliveryTime"} <= deliveries["list"][0].keys()


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_coin_greeks(private_client):
    result = _assert_ok(await private_client.get_coin_greeks(base_coin="BTC"))
    assert "list" in result
