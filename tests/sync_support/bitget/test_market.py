# ruff: noqa: ANN001, ANN201, D100, D103

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


def test_get_spot_market_trades(client):
    res = client.get_spot_market_trades(product_symbol="BTC-USDT-SPOT", limit=5)
    _assert_success(res)
    assert res["data"]


@pytest.mark.parametrize(
    "category,symbol", [("SPOT", "BTC-USDT-SPOT"), ("USDT-FUTURES", "BTC-USDT-SWAP")]
)
def test_uta_market_data(client, category, symbol):
    _assert_success(client.get_uta_instruments(category, product_symbol=symbol))
    _assert_success(client.get_uta_tickers(category, product_symbol=symbol))
    book = client.get_uta_orderbook(category, symbol, limit=5)
    _assert_success(book)
    assert book["data"]["bids"] and book["data"]["asks"]
