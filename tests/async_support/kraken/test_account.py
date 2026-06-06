# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.kraken.client import Client

load_dotenv()

KRAKEN_SPOT_API_KEY = os.getenv("KRAKEN_SPOT_API_KEY")
KRAKEN_SPOT_API_SECRET = os.getenv("KRAKEN_SPOT_API_SECRET")
KRAKEN_FUTURES_API_KEY = os.getenv("KRAKEN_FUTURES_API_KEY")
KRAKEN_FUTURES_API_SECRET = os.getenv("KRAKEN_FUTURES_API_SECRET")

pytestmark = [pytest.mark.asyncio, pytest.mark.private]


@pytest_asyncio.fixture
async def client():
    async with Client(
        spot_api_key=KRAKEN_SPOT_API_KEY,
        spot_api_secret=KRAKEN_SPOT_API_SECRET,
        futures_api_key=KRAKEN_FUTURES_API_KEY,
        futures_api_secret=KRAKEN_FUTURES_API_SECRET,
    ) as client_instance:
        yield client_instance


def _assert_spot_response(response):
    assert isinstance(response, dict)
    assert response.get("error", []) == []
    assert "result" in response
    return response


def _assert_futures_response(response):
    assert isinstance(response, dict)
    assert response.get("result") == "success"
    return response


async def test_spot_account_read_endpoints(client):
    _assert_spot_response(await client.get_spot_account_balance())
    _assert_spot_response(await client.get_spot_trade_balance(asset="USDT"))
    _assert_spot_response(await client.get_spot_open_positions())
    _assert_spot_response(await client.get_spot_ledgers(asset="USDT", without_count=True))
    _assert_spot_response(await client.get_spot_trade_volume(pair="XBTUSDT", fee_info=True))


async def test_spot_trade_history_read_endpoints(client):
    _assert_spot_response(await client.get_spot_open_orders())
    _assert_spot_response(await client.get_spot_closed_orders())
    _assert_spot_response(await client.get_spot_trade_history())


async def test_futures_account_read_endpoints(client):
    assert "accounts" in _assert_futures_response(await client.get_futures_accounts())
    _assert_futures_response(await client.get_futures_open_positions())
    _assert_futures_response(await client.get_futures_fills())


async def test_futures_trade_read_endpoints(client):
    _assert_futures_response(await client.get_futures_open_orders())
