from datetime import datetime, timedelta

import pytest

from dcex.bitmart.client import Client


@pytest.fixture
def client():
    return Client()


def test_get_spot_currencies(client):
    res = client.get_spot_currencies()
    assert res is not None


def test_get_trading_pairs(client):
    res = client.get_trading_pairs()
    assert res is not None


def test_get_trading_pairs_details(client):
    res = client.get_trading_pairs_details()
    assert res is not None


def test_get_ticker_of_all_pairs(client):
    res = client.get_ticker_of_all_pairs()
    assert res is not None


def test_get_ticker_of_a_pair(client):
    res = client.get_ticker_of_a_pair(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_spot_kline(client):
    res = client.get_spot_kline("BTC-USDT-SPOT", "5m")
    assert res is not None


def test_get_depth(client):
    res = client.get_depth(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_contract_kline(client):
    start = int((datetime.now() - timedelta(days=1)).timestamp())
    end = int(datetime.now().timestamp())
    res = client.get_contract_kline("BTC-USDT-SWAP", "5m", start, end)
    assert res is not None


def test_get_contracts_details(client):
    res = client.get_contracts_details(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_open_interest(client):
    res = client.get_open_interest(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_mark_price_kline(client):
    start = int((datetime.now() - timedelta(days=1)).timestamp())
    end = int(datetime.now().timestamp())
    res = client.get_mark_price_kline("BTC-USDT-SWAP", "5m", start, end)
    assert res is not None


def test_get_leverage_bracket(client):
    res = client.get_leverage_bracket(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_current_funding_rate(client):
    res = client.get_current_funding_rate(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_funding_rate_history(client):
    res = client.get_funding_rate_history(product_symbol="BTC-USDT-SWAP", limit=10)
    assert res is not None
