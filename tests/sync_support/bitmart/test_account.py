from dcex.bitmart.client import Client
import os
from dotenv import load_dotenv
import pytest

load_dotenv()

BITMART_API_KEY = os.getenv("BITMART_API_KEY")
BITMART_API_SECRET = os.getenv("BITMART_API_SECRET")
MEMO = os.getenv("BITMART_MEMO")


@pytest.fixture
def client():
    return Client(
        api_key=BITMART_API_KEY,
        api_secret=BITMART_API_SECRET,
        memo=MEMO,
    )


@pytest.mark.private
def test_get_account_balance(client):
    res = client.get_account_balance()
    assert res is not None


@pytest.mark.private
def test_get_account_currencies(client):
    res = client.get_account_currencies()
    assert res is not None


@pytest.mark.private
def test_get_spot_wallet(client):
    res = client.get_spot_wallet()
    assert res is not None


@pytest.mark.private
def test_get_deposit_address(client):
    res = client.get_deposit_address(currency="BTC")
    assert res is not None


@pytest.mark.private
def test_get_withdraw_charge(client):
    res = client.get_withdraw_charge(currency="BTC")
    assert res is not None


@pytest.mark.private
def test_get_deposit_withdraw_history(client):
    res = client.get_deposit_withdraw_history(currency="USDT")
    assert res is not None


@pytest.mark.private
def test_get_deposit_withdraw_history_detail(client):
    res = client.get_deposit_withdraw_history_detail(id="26695771")
    assert res is not None


@pytest.mark.private
def test_get_contract_assets(client):
    res = client.get_contract_assets()
    assert res is not None
