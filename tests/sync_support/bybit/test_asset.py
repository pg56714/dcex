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
def test_get_coin_info(client):
    res = client.get_coin_info()
    assert res is not None


# @pytest.mark.private
# def test_get_sub_uid(client):
#     res = client.get_sub_uid()
#     assert res is not None

@pytest.mark.private
def test_get_spot_asset_info(client):
    res = client.get_spot_asset_info()
    assert res is not None


@pytest.mark.private
def test_get_coins_balance(client):
    res = client.get_coins_balance(accountType="FUND")
    assert res is not None


@pytest.mark.private
def test_get_coin_balance(client):
    res = client.get_coin_balance(accountType="FUND", coin="BTC")
    assert res is not None


@pytest.mark.private
def test_get_withdrawable_amount(client):
    res = client.get_withdrawable_amount(coin="USDT")
    assert res is not None


@pytest.mark.private
def test_get_internal_transfer_records(client):
    res = client.get_internal_transfer_records()
    assert res is not None


@pytest.mark.private
def test_get_universal_transfer_records(client):
    res = client.get_universal_transfer_records()
    assert res is not None


@pytest.mark.private
def test_get_deposit_records(client):
    res = client.get_deposit_records()
    assert res is not None


@pytest.mark.private
def test_get_internal_deposit_records(client):
    res = client.get_internal_deposit_records()
    assert res is not None

# @pytest.mark.private
# def test_get_master_deposit_address(client):
#     res = client.get_master_deposit_address(coin="USDT")
#     assert res is not None


@pytest.mark.private
def test_get_withdrawal_records(client):
    res = client.get_withdrawal_records()
    assert res is not None
