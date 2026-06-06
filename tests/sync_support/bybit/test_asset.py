# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.bybit.client import Client

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


@pytest.mark.private
def test_get_sub_uid(client):
    res = client.get_sub_uid()
    assert res is not None


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
def test_get_transferable_coin(client):
    res = client.get_transferable_coin(
        fromAccountType="FUND",
        toAccountType="UNIFIED",
    )
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
def test_get_sub_deposit_records(client):
    response = client.get_sub_uid()
    members = response.get("result", {}).get("subMembers", [])
    sub_member_id = os.getenv("BYBIT_SUB_MEMBER_ID")
    if not sub_member_id and members:
        sub_member_id = str(members[0]["uid"])
    if not sub_member_id:
        pytest.skip("Set BYBIT_SUB_MEMBER_ID or create a Bybit sub-account.")
    res = client.get_sub_deposit_records(subMemberId=sub_member_id)
    assert res is not None


@pytest.mark.private
def test_get_internal_deposit_records(client):
    res = client.get_internal_deposit_records()
    assert res is not None


@pytest.mark.private
def test_get_master_deposit_address(client):
    res = client.get_master_deposit_address(coin="USDT")
    assert res is not None
