# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.binance.client import Client

load_dotenv()


BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")


@pytest.fixture
def client():
    return Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
    )


@pytest.mark.private
def test_get_account_balance(client):
    res = client.get_account_balance(market_type="spot")
    assert res is not None


@pytest.mark.private
def test_get_futures_account_balance(client):
    res = client.get_account_balance(market_type="swap")
    assert res is not None


@pytest.mark.private
def test_get_futures_account_info(client):
    res = client.get_futures_account_info()
    assert res is not None


@pytest.mark.private
def test_get_wallet_balance(client):
    res = client.get_wallet_balance(quoteAsset="USDT")
    assert isinstance(res, list)


@pytest.mark.private
def test_get_funding_wallet(client):
    res = client.get_funding_wallet(asset="USDT", needBtcValuation=True)
    assert isinstance(res, list)


@pytest.mark.private
def test_get_universal_transfer_history(client):
    res = client.get_universal_transfer_history(type_="FUNDING_MAIN", size=1)
    assert res is not None


@pytest.mark.private
def test_get_income_history(client):
    res = client.get_income_history()
    assert res is not None


@pytest.mark.private
def test_spot_rest_listen_key_is_unavailable(client):
    with pytest.raises(NotImplementedError):
        client.get_listen_key(market_type="spot")


@pytest.mark.private
def test_futures_listen_key_lifecycle(client):
    listen_key = client.get_listen_key(market_type="swap")
    assert listen_key
    assert client.keep_alive_listen_key(listen_key, market_type="swap") is not None
    assert client.close_listen_key(listen_key, market_type="swap") is not None
