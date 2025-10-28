from dcex.okx.client import Client
import pytest


@pytest.fixture
def client():
    return Client()


def test_get_candles_ticks(client):
    res = client.get_candles_ticks(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_orderbook(client):
    res = client.get_orderbook(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_tickers(client):
    res = client.get_tickers(instType="SPOT")
    assert res is not None

def test_get_public_trades(client):
    res = client.get_public_trades(product_symbol="BTC-USDT-SPOT")
    assert res is not None
