# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.okx.client import Client

load_dotenv()

pytestmark = pytest.mark.private


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=os.getenv("OKX_API_KEY"),
        api_secret=os.getenv("OKX_API_SECRET"),
        passphrase=os.getenv("OKX_PASSPHRASE"),
    ) as client_instance:
        yield client_instance


def _assert_ok(response):
    assert response["code"] in ("0", 0), response
    assert "data" in response
    return response


@pytest.mark.asyncio
async def test_subaccount_read_endpoints(client):
    accounts = _assert_ok(await client.get_subaccount_list(limit=20))
    _assert_ok(await client.get_entrusted_subaccount_list())
    if not accounts["data"]:
        return

    sub_account = accounts["data"][0]["subAcct"]
    _assert_ok(await client.get_subaccount_interest_limits(sub_account))
    _assert_ok(await client.get_subaccount_trading_balance(sub_account))
    _assert_ok(await client.get_subaccount_funding_balance(sub_account))
    _assert_ok(await client.get_subaccount_bills(sub_account, limit=20))
