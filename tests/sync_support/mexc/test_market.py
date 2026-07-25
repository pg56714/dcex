# ruff: noqa: ANN001, ANN201, D100, D103

import pytest

from dcex.mexc.client import Client


@pytest.fixture
def client():
    client_instance = Client()
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_contract_success(res) -> None:
    assert res["success"] is True
    assert res["code"] == 0
    assert "data" in res


def test_ping(client):
    res = client.ping()
    assert isinstance(res, dict)


def test_get_spot_time(client):
    res = client.get_spot_time()
    assert res["serverTime"] > 0


def test_get_spot_default_symbols(client):
    res = client.get_spot_default_symbols()
    assert "data" in res


def test_get_spot_exchange_info(client):
    res = client.get_spot_exchange_info(product_symbol="BTC-USDT-SPOT")
    assert res["symbols"]
    assert res["symbols"][0]["symbol"] == "BTCUSDT"


def test_get_spot_orderbook(client):
    res = client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", limit=5)
    assert res["bids"]
    assert res["asks"]


def test_get_spot_recent_trades(client):
    res = client.get_spot_recent_trades(product_symbol="BTC-USDT-SPOT", limit=2)
    assert res


def test_get_spot_agg_trades(client):
    res = client.get_spot_agg_trades(product_symbol="BTC-USDT-SPOT", limit=2)
    assert res


def test_get_spot_klines(client):
    res = client.get_spot_klines(product_symbol="BTC-USDT-SPOT", interval="1m", limit=2)
    assert res


def test_get_spot_avg_price(client):
    res = client.get_spot_avg_price(product_symbol="BTC-USDT-SPOT")
    assert float(res["price"]) > 0


def test_get_spot_ticker_24hr(client):
    res = client.get_spot_ticker_24hr(product_symbol="BTC-USDT-SPOT")
    assert res["symbol"] == "BTCUSDT"


def test_get_spot_ticker_price(client):
    res = client.get_spot_ticker_price(product_symbol="BTC-USDT-SPOT")
    assert res["symbol"] == "BTCUSDT"
    assert float(res["price"]) > 0


def test_get_spot_book_ticker(client):
    res = client.get_spot_book_ticker(product_symbol="BTC-USDT-SPOT")
    assert res["symbol"] == "BTCUSDT"


def test_get_contract_time(client):
    res = client.get_contract_time()
    _assert_contract_success(res)
    assert res["data"] > 0


def test_get_contract_details(client):
    res = client.get_contract_details(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


def test_get_contract_ticker(client):
    res = client.get_contract_ticker(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


def test_get_contract_depth(client):
    res = client.get_contract_depth(product_symbol="BTC-USDT-SWAP", limit=5)
    _assert_contract_success(res)
    assert res["data"]["bids"]
    assert res["data"]["asks"]


def test_get_contract_depth_commits(client):
    res = client.get_contract_depth_commits(product_symbol="BTC-USDT-SWAP", limit=5)
    _assert_contract_success(res)
    assert res["data"]


def test_get_contract_index_price(client):
    res = client.get_contract_index_price(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


def test_get_contract_fair_price(client):
    res = client.get_contract_fair_price(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


def test_get_contract_funding_rate(client):
    res = client.get_contract_funding_rate(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]["symbol"] == "BTC_USDT"


def test_get_contract_kline(client):
    res = client.get_contract_kline(product_symbol="BTC-USDT-SWAP", interval="Min1")
    _assert_contract_success(res)
    assert res["data"]["time"]


def test_get_contract_index_price_kline(client):
    res = client.get_contract_index_price_kline(product_symbol="BTC-USDT-SWAP", interval="Min1")
    _assert_contract_success(res)
    assert res["data"]["time"]


def test_get_contract_fair_price_kline(client):
    res = client.get_contract_fair_price_kline(product_symbol="BTC-USDT-SWAP", interval="Min1")
    _assert_contract_success(res)
    assert res["data"]["time"]


def test_get_contract_deals(client):
    res = client.get_contract_deals(product_symbol="BTC-USDT-SWAP", limit=2)
    _assert_contract_success(res)
    assert res["data"]


def test_get_contract_risk_reverse(client):
    res = client.get_contract_risk_reverse(product_symbol="BTC-USDT-SWAP")
    _assert_contract_success(res)
    assert res["data"]


def test_get_contract_risk_reverse_history(client):
    res = client.get_contract_risk_reverse_history(
        product_symbol="BTC-USDT-SWAP",
        page_num=1,
        page_size=2,
    )
    _assert_contract_success(res)
    assert res["data"]["resultList"]


def test_get_contract_funding_rate_history(client):
    res = client.get_contract_funding_rate_history(
        product_symbol="BTC-USDT-SWAP",
        page_num=1,
        page_size=2,
    )
    _assert_contract_success(res)
    assert res["data"]["resultList"]
