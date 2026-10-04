# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import asyncio
import os
import time
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.binance.client import Client

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


@pytest_asyncio.fixture
async def private_client():
    async with Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET) as client_instance:
        yield client_instance


@pytest_asyncio.fixture(autouse=True)
async def _binance_public_rate_limit() -> None:
    await asyncio.sleep(float(os.getenv("BINANCE_PUBLIC_TEST_DELAY_SECONDS", "2")))


async def _active_btc_option(client) -> dict:
    info = await client.get_options_exchange_info()
    now_ms = int(time.time() * 1000)
    options = [
        row
        for row in info["optionSymbols"]
        if row["underlying"] == "BTCUSDT"
        and row["status"] == "TRADING"
        and int(row["expiryDate"]) > now_ms
    ]
    assert options
    return min(options, key=lambda row: int(row["expiryDate"]))


@pytest.mark.asyncio
async def test_option_market_data_endpoints(client):
    option = await _active_btc_option(client)
    symbol = option["symbol"]

    klines = await client.get_options_klines(symbol, "1h", limit=5)
    assert isinstance(klines, list)
    assert all(len(row) >= 6 for row in klines)

    orderbook = await client.get_options_orderbook(symbol, limit=10)
    assert {"bids", "asks"} <= orderbook.keys()

    trades = await client.get_options_trades(symbol, limit=5)
    assert isinstance(trades, list)
    assert all(row["symbol"] == symbol for row in trades)

    expiration = datetime.fromtimestamp(int(option["expiryDate"]) / 1000, UTC).strftime("%y%m%d")
    open_interest = await client.get_options_open_interest("BTC", expiration)
    assert isinstance(open_interest, list)
    assert open_interest
    assert {"symbol", "sumOpenInterest"} <= open_interest[0].keys()


@pytest.mark.asyncio
async def test_option_history_endpoints(client):
    exercises = await client.get_options_exercise_history(underlying="BTCUSDT", limit=5)
    assert isinstance(exercises, list)
    assert exercises
    assert {"symbol", "strikePrice", "realStrikePrice", "strikeResult"} <= exercises[0].keys()

    block_trades = await client.get_options_block_trades()
    assert isinstance(block_trades, list)
    if block_trades:
        assert {"symbol", "price", "qty"} <= block_trades[0].keys()


@pytest.mark.asyncio
@pytest.mark.private
async def test_dual_investment_read_endpoints(private_client):
    products = await private_client.get_dual_investment_product_list(
        option_type="CALL", exercised_coin="USDT", invest_coin="BTC", page_size=10
    )
    assert isinstance(products, dict)
    assert "list" in products

    accounts = await private_client.check_dual_investment_accounts()
    assert isinstance(accounts, dict)
    assert "totalAmountInUSDT" in accounts

    positions = await private_client.get_dual_investment_positions(page_size=10)
    assert isinstance(positions, dict)
    assert "list" in positions
