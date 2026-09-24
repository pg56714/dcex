# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.kucoin.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")


@pytest.fixture
def client():
    return Client(
        api_key=KUCOIN_API_KEY,
        api_secret=KUCOIN_API_SECRET,
        passphrase=KUCOIN_API_PASSPHRASE,
    )


@pytest.mark.private
def test_get_account_balance(client):
    res = client.get_account_balance()
    assert res is not None


@pytest.mark.private
def test_get_transfer_quotas(client):
    res = client.get_transfer_quotas(currency="USDT", account_type="MAIN")
    assert res is not None


@pytest.mark.private
def test_get_futures_account(client):
    res = client.get_futures_account(currency="USDT")
    assert res is not None


@pytest.mark.private
def test_get_futures_positions(client):
    res = client.get_futures_positions(currency="USDT")
    assert res is not None


@pytest.mark.private
def test_get_futures_position(client):
    res = client.get_futures_position(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.private
def test_get_futures_position_mode(client):
    res = client.get_futures_position_mode()
    assert res is not None


@pytest.mark.private
def test_get_futures_cross_margin_leverage(client):
    res = client.get_futures_cross_margin_leverage(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.private
def test_get_margin_account_read_endpoints(client):
    try:
        assert client.get_cross_margin_account() is not None
    except FailedRequestError as exc:
        if "[101030]" in str(exc):
            pytest.skip("KuCoin margin trading is not enabled for this account.")
        raise
    assert client.get_isolated_margin_account(product_symbol="BTC-USDT-SPOT") is not None


@pytest.mark.private
def test_get_margin_borrowing_read_endpoints(client):
    assert client.get_margin_borrow_interest_rate(currency="USDT") is not None
    assert client.get_margin_borrow_history(currency="USDT", pageSize=20) is not None
    assert client.get_margin_repay_history(currency="USDT", pageSize=20) is not None
    assert client.get_margin_interest_history(currency="USDT", pageSize=20) is not None


@pytest.mark.private
def test_get_margin_lending_read_endpoints(client):
    assert client.get_margin_loan_market(currency="USDT") is not None
    assert (
        client.get_margin_lending_purchase_orders(status="DONE", currency="USDT", pageSize=20)
        is not None
    )
    assert (
        client.get_margin_lending_redeem_orders(status="DONE", currency="USDT", pageSize=20)
        is not None
    )


@pytest.mark.private
def test_get_earn_read_endpoints(client):
    assert client.get_earn_savings_products(currency="USDT") is not None
    assert client.get_earn_promotion_products(currency="USDT") is not None
    assert client.get_earn_staking_products() is not None
    assert client.get_earn_kcs_staking_products(currency="KCS") is not None
    assert client.get_earn_eth_staking_products(currency="ETH") is not None
    assert client.get_earn_account_holdings(currentPage=1, pageSize=20) is not None
    assert (
        client.get_structured_earn_orders(categories="DUAL_CLASSIC", currentPage=1, pageSize=20)
        is not None
    )


@pytest.mark.private
def test_get_classic_subaccount_read_endpoints(client):
    summary = client.get_subaccounts()
    assert summary is not None
    sub_user_ids = [
        item.get("userId")
        for item in summary.get("data", {}).get("items", [])
        if item.get("userId")
    ]
    if sub_user_ids:
        assert client.get_subaccount_balance(sub_user_ids[0]) is not None
    assert client.get_spot_subaccount_balances() is not None
    assert client.get_futures_subaccount_balances(currency="USDT") is not None


@pytest.mark.private
def test_get_uta_subaccount_read_endpoints(client):
    assert client.get_uta_subaccounts() is not None
    assert client.get_uta_subaccount_currency_assets() is not None
