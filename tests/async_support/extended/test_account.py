# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.extended.client import Client

load_dotenv()

pytestmark = [pytest.mark.asyncio, pytest.mark.private]


@pytest_asyncio.fixture
async def client():
    async with Client(preload_product_table=False, timeout=20) as client_instance:
        yield client_instance


def _assert_response(response: object) -> dict | list:
    assert isinstance(response, dict | list)
    return response


async def test_account_read_endpoints(client):
    _assert_response(await client.get_account_details())
    _assert_response(await client.get_sub_accounts())
    _assert_response(await client.get_balance())
    _assert_response(await client.get_spot_balances())
    _assert_response(await client.get_asset_operations(limit=20))


async def test_position_trade_and_fee_read_endpoints(client):
    _assert_response(await client.get_positions())
    _assert_response(await client.get_positions_history(limit=20))
    _assert_response(await client.get_trades_history(limit=20))
    _assert_response(
        await client.get_funding_payments(
            startTime=int(time.time() * 1000) - 30 * 24 * 60 * 60 * 1000,
            limit=20,
        )
    )
    _assert_response(await client.get_leverage())
    _assert_response(await client.get_fees())
    _assert_response(await client.get_rebates())
    _assert_response(await client.get_bridge_config())


async def test_order_read_endpoints(client):
    _assert_response(await client.get_open_orders())
    _assert_response(await client.get_orders_history(limit=20))
