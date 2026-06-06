# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.okx.client import Client

load_dotenv()

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")


@pytest.fixture
def client():
    return Client(
        api_key=OKX_API_KEY,
        api_secret=OKX_API_SECRET,
        passphrase=OKX_PASSPHRASE,
    )


@pytest.mark.private
def test_get_currencies(client):
    res = client.get_currencies()
    assert res is not None


@pytest.mark.private
def test_get_balances(client):
    res = client.get_balances()
    assert res is not None


@pytest.mark.private
def test_get_asset_valuation(client):
    res = client.get_asset_valuation()
    assert res is not None


@pytest.mark.private
def test_get_bills(client):
    res = client.get_bills()
    assert res is not None


@pytest.mark.private
def test_get_deposit_address(client):
    res = client.get_deposit_address(ccy="BTC")
    assert res is not None


@pytest.mark.private
def test_get_deposit_history(client):
    res = client.get_deposit_history()
    assert res is not None


@pytest.mark.private
def test_get_deposit_withdraw_status(client):
    history = client.get_deposit_history(ccy="USDT")
    deposit = next(
        (
            item
            for item in history.get("data", [])
            if isinstance(item, dict)
            and item.get("txId")
            and item.get("ccy")
            and item.get("to")
            and item.get("chain")
        ),
        None,
    )
    if deposit is None:
        pytest.skip("OKX account has no complete USDT deposit record to query.")
    res = client.get_deposit_withdraw_status(
        txId=deposit["txId"],
        ccy=deposit["ccy"],
        to=deposit["to"],
        chain=deposit["chain"],
    )
    assert res is not None


@pytest.mark.private
def test_get_exchange_list(client):
    res = client.get_exchange_list()
    assert res is not None


@pytest.mark.private
def test_post_monthly_statement(client):
    res = client.post_monthly_statement(month="Mar")
    assert res is not None


@pytest.mark.private
def test_get_monthly_statement(client):
    res = client.get_monthly_statement(month="Mar")
    assert res is not None


@pytest.mark.private
def test_get_convert_currencies(client):
    res = client.get_convert_currencies()
    assert res is not None


@pytest.mark.private
def test_get_convert_history(client):
    res = client.get_convert_history()
    assert res is not None
