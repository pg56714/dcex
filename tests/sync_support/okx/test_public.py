import pytest

from dcex.okx.client import Client


@pytest.fixture
def client():
    return Client()


def test_get_public_instruments(client):
    res = client.get_public_instruments(instType="SPOT")
    assert res is not None


def test_get_funding_rate(client):
    res = client.get_funding_rate(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_funding_rate_history(client):
    res = client.get_funding_rate_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_open_interest(client):
    res = client.get_open_interest(instType="SWAP", product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_position_tiers(client):
    res = client.get_position_tiers(
        instType="SWAP", tdMode="cross", product_symbol="BTC-USDT-SWAP"
    )
    assert res is not None


def test_get_trading_data_support_coin(client):
    res = client.get_trading_data_support_coin()
    assert res is not None


def test_get_taker_volume(client):
    res = client.get_taker_volume(ccy="BTC", instType="SPOT")
    assert res is not None


def test_get_contract_taker_volume(client):
    res = client.get_contract_taker_volume(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_long_short_ratio(client):
    res = client.get_long_short_ratio(ccy="BTC")
    assert res is not None


def test_get_contract_long_short_ratio(client):
    res = client.get_contract_long_short_ratio(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_top_trader_long_short_account_ratio(client):
    res = client.get_top_trader_long_short_account_ratio(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_top_trader_long_short_position_ratio(client):
    res = client.get_top_trader_long_short_position_ratio(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_contracts_open_interest_and_volume(client):
    res = client.get_contracts_open_interest_and_volume(ccy="BTC")
    assert res is not None


def test_get_contract_open_interest_history(client):
    res = client.get_contract_open_interest_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None
