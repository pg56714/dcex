# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.okx.client import Client

load_dotenv()

pytestmark = pytest.mark.private


@pytest.fixture
def client():
    return Client(
        api_key=os.getenv("OKX_API_KEY"),
        api_secret=os.getenv("OKX_API_SECRET"),
        passphrase=os.getenv("OKX_PASSPHRASE"),
    )


def _assert_ok(response):
    assert response["code"] in ("0", 0), response
    assert "data" in response
    return response


def test_subaccount_read_endpoints(client):
    accounts = _assert_ok(client.get_subaccount_list(limit=20))
    _assert_ok(client.get_entrusted_subaccount_list())
    if not accounts["data"]:
        return

    sub_account = accounts["data"][0]["subAcct"]
    _assert_ok(client.get_subaccount_interest_limits(sub_account))
    _assert_ok(client.get_subaccount_trading_balance(sub_account))
    _assert_ok(client.get_subaccount_funding_balance(sub_account))
    _assert_ok(client.get_subaccount_bills(sub_account, limit=20))
