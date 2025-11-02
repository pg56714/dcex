from dcex.binance.client import Client
import pytest


@pytest.fixture
def client():
    return Client()


def test_get_spot_exchange_info(client):
    res = client.get_spot_exchange_info(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_futures_exchange_info(client):
    res = client.get_futures_exchange_info()
    assert res is not None


def test_get_futures_ticker(client):
    res = client.get_futures_ticker(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_klines(client):
    res = client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m")
    assert res is not None


def test_get_futures_premium_index(client):
    res = client.get_futures_premium_index(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_futures_funding_rate(client):
    res = client.get_futures_funding_rate(product_symbol="BTC-USDT-SWAP")
    assert res is not None
