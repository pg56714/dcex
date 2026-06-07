# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest

from dcex.bitget.client import Client


@pytest.fixture
def client():
    client_instance = Client()
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_success(res) -> None:
    assert res["code"] == "00000"
    assert "data" in res


def test_get_spot_coins(client):
    res = client.get_spot_coins(coin="USDT")
    _assert_success(res)
    assert res["data"]


def test_get_spot_symbols(client):
    res = client.get_spot_symbols(product_symbol="BTC-USDT-SPOT")
    _assert_success(res)
    assert res["data"]


def test_get_spot_tickers(client):
    res = client.get_spot_tickers(product_symbol="BTC-USDT-SPOT")
    _assert_success(res)
    assert res["data"]


def test_get_spot_orderbook(client):
    res = client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", limit=5)
    _assert_success(res)
    assert res["data"]["bids"]
    assert res["data"]["asks"]


def test_get_spot_kline(client):
    res = client.get_spot_kline(product_symbol="BTC-USDT-SPOT", granularity="1min", limit=5)
    _assert_success(res)
    assert res["data"]


def test_get_spot_history_kline(client):
    end_time = int(time.time() * 1000)
    start_time = end_time - 10 * 60 * 1000
    res = client.get_spot_history_kline(
        product_symbol="BTC-USDT-SPOT",
        granularity="1min",
        startTime=start_time,
        endTime=end_time,
        limit=5,
    )
    _assert_success(res)
    assert res["data"]


def test_get_spot_recent_trades(client):
    res = client.get_spot_recent_trades(product_symbol="BTC-USDT-SPOT", limit=5)
    _assert_success(res)
    assert res["data"]


def test_get_spot_market_trades(client):
    res = client.get_spot_market_trades(product_symbol="BTC-USDT-SPOT", limit=5)
    _assert_success(res)
    assert res["data"]


def test_get_futures_contracts(client):
    res = client.get_futures_contracts(product_symbol="BTC-USDT-SWAP")
    _assert_success(res)
    assert res["data"]


def test_get_futures_ticker(client):
    res = client.get_futures_ticker(product_symbol="BTC-USDT-SWAP")
    _assert_success(res)
    assert res["data"]


def test_get_futures_tickers(client):
    res = client.get_futures_tickers()
    _assert_success(res)
    assert res["data"]


def test_get_futures_orderbook(client):
    res = client.get_futures_orderbook(product_symbol="BTC-USDT-SWAP", limit=5)
    _assert_success(res)
    assert res["data"]["bids"]
    assert res["data"]["asks"]


def test_get_futures_kline(client):
    res = client.get_futures_kline(product_symbol="BTC-USDT-SWAP", granularity="1m", limit=5)
    _assert_success(res)
    assert res["data"]


def test_get_futures_history_kline(client):
    res = client.get_futures_history_kline(
        product_symbol="BTC-USDT-SWAP",
        granularity="1m",
        limit=5,
    )
    _assert_success(res)
    assert res["data"]


def test_get_futures_recent_trades(client):
    res = client.get_futures_recent_trades(product_symbol="BTC-USDT-SWAP", limit=5)
    _assert_success(res)
    assert res["data"]


def test_get_futures_current_funding_rate(client):
    res = client.get_futures_current_funding_rate(product_symbol="BTC-USDT-SWAP")
    _assert_success(res)
    assert res["data"]


def test_get_futures_history_funding_rate(client):
    res = client.get_futures_history_funding_rate(product_symbol="BTC-USDT-SWAP", pageSize=5)
    _assert_success(res)
    assert res["data"]


def test_get_futures_open_interest(client):
    res = client.get_futures_open_interest(product_symbol="BTC-USDT-SWAP")
    _assert_success(res)
    assert res["data"]
