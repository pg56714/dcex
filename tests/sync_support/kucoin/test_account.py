# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.kucoin.client import Client

load_dotenv()

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")


@pytest.fixture
def client():
    return Client(
        api_key=KUCOIN_API_KEY,
        api_secret=KUCOIN_API_SECRET,
        passphrase=KUCOIN_API_PASSPHRASE,
    )


@pytest.mark.private
def test_get_account_balance(client):
    res = client.get_account_balance()
    assert res is not None


@pytest.mark.private
def test_get_futures_account(client):
    res = client.get_futures_account(currency="USDT")
    assert res is not None


@pytest.mark.private
def test_get_futures_positions(client):
    res = client.get_futures_positions(currency="USDT")
    assert res is not None


@pytest.mark.private
def test_get_futures_position(client):
    res = client.get_futures_position(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.private
def test_get_futures_position_mode(client):
    res = client.get_futures_position_mode()
    assert res is not None
