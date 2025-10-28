from dcex.okx.client import Client
import os
import pytest
from dotenv import load_dotenv

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
def test_get_order_list(client):
    res = client.get_order_list(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.private
def test_get_orders_history(client):
    res = client.get_orders_history(instType="SPOT")
    assert res is not None


@pytest.mark.private
def test_get_orders_history_archive(client):
    res = client.get_orders_history_archive(instType="SPOT")
    assert res is not None


@pytest.mark.private
def test_get_fills(client):
    res = client.get_fills()
    assert res is not None


@pytest.mark.private
def test_get_fills_history(client):
    res = client.get_fills_history(instType="SPOT")
    assert res is not None


@pytest.mark.private
def test_get_account_rate_limit(client):
    res = client.get_account_rate_limit()
    assert res is not None
