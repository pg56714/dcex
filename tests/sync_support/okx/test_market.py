# ruff: noqa: ANN001, ANN201, D100, D103

import pytest

from dcex.okx.client import Client


@pytest.fixture
def client():
    return Client()


def test_get_candles_ticks(client):
    res = client.get_candles_ticks(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_orderbook(client):
    res = client.get_orderbook(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_tickers(client):
    res = client.get_tickers(instType="SPOT")
    assert res is not None


def test_stock_xperp_instrument_metadata(client):
    res = client.get_public_instruments(instType="FUTURES")
    stock_xperps = [
        market
        for market in res["data"]
        if market.get("ruleType") == "xperp" and market.get("instCategory") == "3"
    ]
    assert stock_xperps
    assert all(float(market["ctVal"]) > 0 for market in stock_xperps)


def test_get_public_trades(client):
    res = client.get_public_trades(product_symbol="BTC-USDT-SPOT")
    assert res is not None
