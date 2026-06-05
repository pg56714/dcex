# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.bingx.client import Client

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")


@pytest.fixture
def client():
    return Client(
        api_key=BINGX_API_KEY,
        api_secret=BINGX_API_SECRET,
    )


@pytest.mark.private
def test_get_swap_account_balance(client):
    res = client.get_swap_account_balance()
    assert res is not None


@pytest.mark.private
def test_get_account_balance(client):
    res = client.get_account_balance()
    assert res is not None


@pytest.mark.private
def test_get_spot_account_balance(client):
    res = client.get_spot_account_balance()
    assert res is not None


@pytest.mark.private
def test_get_fund_account_balance(client):
    res = client.get_fund_account_balance(asset="USDT")
    assert res is not None


@pytest.mark.private
def test_get_all_account_balance(client):
    res = client.get_all_account_balance()
    assert res is not None


@pytest.mark.private
def test_get_account_uid(client):
    res = client.get_account_uid()
    assert res is not None


@pytest.mark.private
def test_get_api_key_info(client):
    uid = client.get_account_uid()["data"]["uid"]
    res = client.get_api_key_info(uid=uid)
    assert res is not None


@pytest.mark.private
def test_get_transferable_coins_to_spot(client):
    res = client.get_transferable_coins(fromAccount="fund", toAccount="spot")
    assert res is not None


@pytest.mark.private
def test_get_transferable_coins_to_swap(client):
    res = client.get_transferable_coins(fromAccount="fund", toAccount="USDTMPerp")
    assert res is not None


@pytest.mark.private
def test_get_asset_transfer_records(client):
    res = client.get_asset_transfer_records(
        fromAccount="fund",
        toAccount="spot",
        pageSize=5,
    )
    assert res is not None


@pytest.mark.private
def test_get_open_positions(client):
    res = client.get_open_positions(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.private
def test_get_fund_flow(client):
    res = client.get_fund_flow(limit=5)
    assert res is not None


@pytest.mark.private
def test_get_listen_key(client):
    res = client.get_listen_key()
    assert res is not None


@pytest.mark.private
def test_keep_alive_listen_key(client):
    listen_key = client.get_listen_key()
    res = client.keep_alive_listen_key(listen_key)
    assert res is not None
