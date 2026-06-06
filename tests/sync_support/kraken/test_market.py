# ruff: noqa: ANN001, ANN201, D100, D103

import pytest

from dcex.kraken.client import Client


@pytest.fixture
def client():
    client_instance = Client()
    try:
        yield client_instance
    finally:
        client_instance.close()


def test_get_server_time(client):
    res = client.get_server_time()
    assert res["result"]["unixtime"] > 0


def test_get_spot_asset_pairs(client):
    res = client.get_spot_asset_pairs(pair="XBTUSDT")
    assert "XBTUSDT" in res["result"]


def test_get_spot_ticker(client):
    res = client.get_spot_ticker(product_symbol="BTC-USDT-SPOT")
    assert res["result"]


def test_get_spot_orderbook(client):
    res = client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", count=5)
    assert res["result"]


def test_get_spot_public_trades(client):
    res = client.get_spot_public_trades(product_symbol="BTC-USDT-SPOT")
    assert res["result"]


def test_get_spot_kline(client):
    res = client.get_spot_kline(product_symbol="BTC-USDT-SPOT", interval=1)
    assert res["result"]


def test_get_futures_instruments(client):
    res = client.get_futures_instruments(contractType="flexible_futures")
    assert res["result"] == "success"
    assert res["instruments"]


def test_get_futures_tickers(client):
    res = client.get_futures_tickers(product_symbol="BTC-USD-SWAP")
    assert res["result"] == "success"
    assert res["tickers"]


def test_get_futures_orderbook(client):
    res = client.get_futures_orderbook(product_symbol="BTC-USD-SWAP")
    assert res["result"] == "success"
    assert res["orderBook"]


def test_get_futures_public_trades(client):
    res = client.get_futures_public_trades(product_symbol="BTC-USD-SWAP")
    assert res["result"] == "success"
    assert res["history"]


def test_get_futures_kline(client):
    res = client.get_futures_kline(product_symbol="BTC-USD-SWAP", timeframe="1m", count=5)
    assert res["candles"]
