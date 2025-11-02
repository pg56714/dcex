from dcex.binance.client import Client
import os
from dotenv import load_dotenv
import pytest

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
def test_get_income_history(client):
    res = client.get_income_history()
    assert res is not None
