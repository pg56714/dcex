from dcex.bybit.client import Client
import os
from dotenv import load_dotenv
import pytest

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")


@pytest.fixture
def client():
    return Client(
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    )


@pytest.mark.private
def test_get_open_orders(client):
    res = client.get_open_orders()
    assert res is not None


@pytest.mark.private
def test_get_order_history(client):
    res = client.get_order_history()
    assert res is not None


@pytest.mark.private
def test_get_execution_list(client):
    res = client.get_execution_list()
    assert res is not None


@pytest.mark.private
def test_get_borrow_quota(client):
    res = client.get_borrow_quota(product_symbol="BTC-USDT-SWAP", side="Buy")
    assert res is not None


@pytest.mark.private
def test_get_vip_margin_data(client):
    res = client.get_vip_margin_data()
    assert res is not None


@pytest.mark.private
def test_get_collateral(client):
    res = client.get_collateral()
    assert res is not None


@pytest.mark.private
def test_get_historical_interest_rate(client):
    res = client.get_historical_interest_rate(currency="USDT")
    assert res is not None


@pytest.mark.private
def test_get_status_and_leverage(client):
    res = client.get_status_and_leverage()
    assert res is not None
