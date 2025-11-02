from datetime import datetime, timedelta
from dcex.bitmart.client import Client
import pytest


@pytest.fixture
def client():
    return Client()


def test_get_spot_currencies(client):
    res = client.get_spot_currencies()
    assert res is not None


def test_get_trading_pairs(client):
    res = client.get_trading_pairs()
    assert res is not None


def test_get_trading_pairs_details(client):
    res = client.get_trading_pairs_details()
    assert res is not None


def test_get_ticker_of_all_pairs(client):
    res = client.get_ticker_of_all_pairs()
    assert res is not None


def test_get_ticker_of_a_pair(client):
    res = client.get_ticker_of_a_pair(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_spot_kline(client):
    res = client.get_spot_kline("BTC-USDT-SPOT", "5m")
    assert res is not None


def test_get_depth(client):
    res = client.get_depth(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_contract_kline(client):
    start = int((datetime.now() - timedelta(days=1)).timestamp())
    end = int(datetime.now().timestamp())
    res = client.get_contract_kline("BTC-USDT-SWAP", "5m", start, end)
    assert res is not None
