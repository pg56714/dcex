import os
from dotenv import load_dotenv
import pytest
from dcex.gateio.client import Client

load_dotenv()


@pytest.fixture
def client():
    return Client(
        api_key=os.getenv("GATEIO_API_KEY"),
        api_secret=os.getenv("GATEIO_API_SECRET"),
    )


@pytest.mark.private
def test_get_futures_account(client):
    res = client.get_futures_account()
    assert res is not None


@pytest.mark.private
def test_get_futures_account_book(client):
    res = client.get_futures_account_book()
    assert res is not None


@pytest.mark.private
def test_get_delivery_account(client):
    res = client.get_delivery_account()
    assert res is not None


@pytest.mark.private
def test_get_delivery_account_book(client):
    res = client.get_delivery_account_book()
    assert res is not None


@pytest.mark.private
def test_get_spot_account(client):
    res = client.get_spot_account(ccy="btc")
    assert res is not None


@pytest.mark.private
def test_get_spot_account_book(client):
    res = client.get_spot_account_book()
    assert res is not None
