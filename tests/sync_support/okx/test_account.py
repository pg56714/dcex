from dcex.okx.client import Client
import os
from dotenv import load_dotenv
import pytest

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
def test_get_account_instruments(client):
    res = client.get_account_instruments(instType="SPOT", product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.private
def test_get_account_balance(client):
    res = client.get_account_balance()
    assert res is not None


@pytest.mark.private
def test_get_positions(client):
    res = client.get_positions(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.private
def test_get_positions_history(client):
    res = client.get_positions_history(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.private
def test_get_position_risk(client):
    res = client.get_position_risk()
    assert res is not None


@pytest.mark.private
def test_get_account_bills(client):
    res = client.get_account_bills(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.private
def test_get_account_bills_archive(client):
    res = client.get_account_bills_archive(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.private
def test_post_account_bills_history_archive(client):
    res = client.post_account_bills_history_archive(year="2025", quarter="Q1")
    assert res is not None


@pytest.mark.private
def test_get_account_bills_history_archive(client):
    res = client.get_account_bills_history_archive(year="2025", quarter="Q1")
    assert res is not None


@pytest.mark.private
def test_get_account_config(client):
    res = client.get_account_config()
    assert res is not None


@pytest.mark.private
def test_set_position_mode(client):
    res = client.set_position_mode(posMode="net_mode")
    assert res is not None


@pytest.mark.private
def test_get_max_order_size(client):
    res = client.get_max_order_size(product_symbol="BTC-USDT-SPOT", tdMode="isolated")
    assert res is not None


@pytest.mark.private
def test_get_max_avail_size(client):
    res = client.get_max_avail_size(product_symbol="BTC-USDT-SPOT", tdMode="cash")
    assert res is not None


@pytest.mark.private
def test_get_leverage(client):
    res = client.get_leverage(product_symbol="BTC-USDT-SWAP", mgnMode="cross")
    assert res is not None


@pytest.mark.private
def test_get_adjust_leverage(client):
    res = client.get_adjust_leverage(product_symbol="BTC-USDT-SWAP", instType="SWAP", mgnMode="cross", lever="3")
    assert res is not None


@pytest.mark.private
def test_get_max_loan(client):
    res = client.get_max_loan(product_symbol="BTC-USDT-SPOT", mgnMode="cross", mgnCcy="USDT")
    assert res is not None


@pytest.mark.private
def test_get_fee_rates(client):
    res = client.get_fee_rates(product_symbol="BTC-USDT-SPOT", instType="SPOT")
    assert res is not None


@pytest.mark.private
def test_get_interest_accrued(client):
    res = client.get_interest_accrued(product_symbol="BTC-USDT-SPOT")
    assert res is not None


@pytest.mark.private
def test_get_interest_rate(client):
    res = client.get_interest_rate()
    assert res is not None


@pytest.mark.private
def test_set_greeks(client):
    res = client.set_greeks(greeksType="PA")
    assert res is not None


@pytest.mark.private
def test_get_max_withdrawal(client):
    res = client.get_max_withdrawal()
    assert res is not None


@pytest.mark.private
def test_get_interest_limits(client):
    res = client.get_interest_limits()
    assert res is not None


@pytest.mark.private
def test_set_leverage(client):
    res = client.set_leverage(lever="10", mgnMode="isolated", product_symbol="BTC-USDT-SWAP")
    assert res is not None
