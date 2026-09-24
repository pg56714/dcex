# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.binance.client import Client

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
def test_get_futures_account_balance(client):
    res = client.get_account_balance(market_type="swap")
    assert res is not None


@pytest.mark.private
def test_get_futures_account_info(client):
    res = client.get_futures_account_info()
    assert res is not None


@pytest.mark.private
def test_get_wallet_balance(client):
    res = client.get_wallet_balance(quoteAsset="USDT")
    assert isinstance(res, list)


@pytest.mark.private
def test_get_funding_wallet(client):
    res = client.get_funding_wallet(asset="USDT", needBtcValuation=True)
    assert isinstance(res, list)


@pytest.mark.private
def test_get_universal_transfer_history(client):
    res = client.get_universal_transfer_history(type_="FUNDING_MAIN", size=1)
    assert res is not None


@pytest.mark.private
def test_get_income_history(client):
    res = client.get_income_history()
    assert res is not None


@pytest.mark.private
def test_get_margin_market_metadata(client):
    assert isinstance(client.get_all_margin_assets(), list)
    assert isinstance(client.get_all_cross_margin_pairs(), list)
    assert isinstance(client.get_all_isolated_margin_symbols(), list)
    assert client.get_margin_price_index("BTC-USDT-SPOT") is not None


@pytest.mark.private
def test_get_margin_account_and_history(client):
    assert client.get_cross_margin_account() is not None
    assert client.get_margin_borrow_repay_records("BORROW", size=1) is not None
    assert client.get_margin_interest_history(size=1) is not None
    assert isinstance(client.get_open_margin_orders(), list)


@pytest.mark.private
def test_get_simple_earn_read_endpoints(client):
    assert client.get_simple_earn_account() is not None
    assert client.get_flexible_earn_products(asset="USDT", size=1) is not None
    assert client.get_locked_earn_products(asset="USDT", size=1) is not None
    assert client.get_flexible_earn_positions(asset="USDT", size=1) is not None
    assert client.get_locked_earn_positions(asset="USDT", size=1) is not None


@pytest.mark.private
def test_get_crypto_loan_read_endpoints(client):
    assert client.get_flexible_loan_assets("USDT") is not None
    assert client.get_flexible_loan_collateral_assets("BTC") is not None
    assert client.get_flexible_loan_ongoing_orders(limit=1) is not None
    assert client.get_flexible_loan_borrow_history(limit=1) is not None
    assert client.get_flexible_loan_repayment_history(limit=1) is not None
    assert client.get_flexible_loan_liquidation_history(limit=1) is not None


@pytest.mark.private
def test_get_staking_read_endpoints(client):
    assert client.get_eth_staking_account() is not None
    assert client.get_eth_staking_quota() is not None
    assert client.get_eth_staking_history(size=1) is not None
    assert client.get_sol_staking_account() is not None
    assert client.get_sol_staking_quota() is not None
    assert client.get_sol_staking_history(size=1) is not None
    assert client.get_onchain_yields_account() is not None
    assert client.get_onchain_yields_products(size=1) is not None
    assert client.get_onchain_yields_positions(size=1) is not None
    assert client.get_soft_staking_products(size=1) is not None


@pytest.mark.private
def test_get_subaccount_read_endpoints(client):
    assert client.get_subaccounts(limit=1) is not None
    assert client.get_subaccount_status() is not None
    assert client.get_subaccount_spot_summary(size=1) is not None
    assert client.get_subaccount_margin_summary() is not None
    assert client.get_subaccount_futures_summary(limit=1) is not None


@pytest.mark.private
def test_spot_rest_listen_key_is_unavailable(client):
    with pytest.raises(NotImplementedError):
        client.get_listen_key(market_type="spot")


@pytest.mark.private
def test_futures_listen_key_lifecycle(client):
    listen_key = client.get_listen_key(market_type="swap")
    assert listen_key
    assert client.keep_alive_listen_key(listen_key, market_type="swap") is not None
    assert client.close_listen_key(listen_key, market_type="swap") is not None
