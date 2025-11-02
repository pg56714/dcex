from dcex.bybit.client import Client
import pytest


@pytest.fixture
def client():
    return Client()


def test_get_instruments_info(client):
    res = client.get_instruments_info(category="spot")
    assert res is not None


def test_get_kline(client):
    res = client.get_kline(
        product_symbol="BTC-USDT-SPOT",
        interval="1m",
    )
    assert res is not None


def test_get_orderbook(client):
    res = client.get_orderbook(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_tickers(client):
    res = client.get_tickers()
    assert res is not None


def test_get_funding_rate_history(client):
    res = client.get_funding_rate_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None
