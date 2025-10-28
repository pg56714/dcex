from dcex.okx.client import Client
import pytest


@pytest.fixture
def client():
    return Client()


def test_get_public_instruments(client):
    res = client.get_public_instruments(instType="SPOT")
    assert res is not None


def test_get_funding_rate(client):
    res = client.get_funding_rate(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_funding_rate_history(client):
    res = client.get_funding_rate_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None
