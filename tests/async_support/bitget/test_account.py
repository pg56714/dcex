# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bitget.client import Client

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

pytestmark = pytest.mark.private


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BITGET_API_KEY,
        api_secret=BITGET_API_SECRET,
        passphrase=BITGET_PASSPHRASE,
    ) as client_instance:
        yield client_instance


def _assert_ok(response) -> dict:
    assert isinstance(response, dict)
    assert response["code"] == "00000", response
    assert "data" in response
    return response


@pytest.mark.asyncio
async def test_common_account_read_endpoints(client):
    _assert_ok(await client.get_all_account_balance())
    _assert_ok(await client.get_funding_assets(coin="USDT"))


@pytest.mark.asyncio
async def test_spot_account_read_endpoints(client):
    end_time = int(time.time() * 1000)
    start_time = end_time - 7 * 24 * 60 * 60 * 1000

    _assert_ok(await client.get_spot_account_info())
    _assert_ok(await client.get_spot_account_assets(coin="USDT"))
    _assert_ok(await client.get_spot_account_bills(coin="USDT", limit=20))
    _assert_ok(await client.get_transferable_coins(fromType="spot", toType="usdt_futures"))
    _assert_ok(await client.get_transfer_records(coin="USDT", limit=20))
    _assert_ok(
        await client.get_deposit_records(
            coin="USDT",
            startTime=start_time,
            endTime=end_time,
            limit=20,
        )
    )


@pytest.mark.asyncio
async def test_futures_account_read_endpoints(client):
    _assert_ok(await client.get_futures_accounts())
    _assert_ok(await client.get_futures_account(product_symbol="BTC-USDT-SWAP"))
    _assert_ok(await client.get_futures_account_bills(limit=20))
    _assert_ok(await client.get_futures_positions())
    _assert_ok(await client.get_futures_position(product_symbol="BTC-USDT-SWAP"))


@pytest.mark.asyncio
async def test_private_trade_read_endpoints(client):
    _assert_ok(await client.get_spot_open_orders(product_symbol="BTC-USDT-SPOT", limit=20))
    _assert_ok(await client.get_spot_history_orders(product_symbol="BTC-USDT-SPOT", limit=20))
    _assert_ok(await client.get_spot_fills(product_symbol="BTC-USDT-SPOT", limit=20))
    _assert_ok(await client.get_futures_open_orders(product_symbol="BTC-USDT-SWAP", limit=20))
    _assert_ok(await client.get_futures_history_orders(product_symbol="BTC-USDT-SWAP", limit=20))
    _assert_ok(await client.get_futures_fills(product_symbol="BTC-USDT-SWAP", limit=20))
