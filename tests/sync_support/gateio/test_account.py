import os

import pytest
from dotenv import load_dotenv

from dcex.gateio.client import Client

load_dotenv()


@pytest.fixture
def client():
    return Client(
        api_key=os.getenv("GATEIO_API_KEY"),
        api_secret=os.getenv("GATEIO_API_SECRET"),
    )


@pytest.mark.private
def test_get_futures_account(client):
    res = client.get_futures_account()
    assert res is not None


@pytest.mark.private
def test_get_total_balance(client):
    res = client.get_total_balance(currency="USDT")
    assert res is not None


@pytest.mark.private
def test_get_unified_accounts(client):
    res = client.get_unified_accounts()
    assert res is not None


@pytest.mark.private
def test_get_futures_account_book(client):
    res = client.get_futures_account_book()
    assert res is not None


@pytest.mark.private
def test_get_delivery_account(client):
    res = client.get_delivery_account()
    assert res is not None


@pytest.mark.private
def test_get_delivery_account_book(client):
    res = client.get_delivery_account_book()
    assert res is not None


@pytest.mark.private
def test_get_spot_account(client):
    res = client.get_spot_account(ccy="btc")
    assert res is not None


@pytest.mark.private
def test_get_spot_account_book(client):
    res = client.get_spot_account_book()
    assert res is not None


@pytest.mark.private
def test_get_spot_fee(client):
    res = client.get_spot_fee(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.private
def test_get_spot_batch_fee(client):
    res = client.get_spot_batch_fee(["BTC-USDT-SPOT", "ETH-USDT-SPOT"])
    assert res is not None
