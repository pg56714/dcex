import pytest
from dotenv import load_dotenv

from dcex.gateio.client import Client

load_dotenv()


@pytest.fixture
def client():
    return Client()


def _delivery_product_symbol(client):
    contracts = client.get_all_delivery_contracts()
    contract = next(row for row in contracts if not row.get("in_delisting"))
    return "-".join(contract["name"].split("_")) + "-SWAP"


def test_get_all_futures_contracts(client):
    res = client.get_all_futures_contracts()
    assert res is not None


def test_get_a_single_futures_contract(client):
    res = client.get_a_single_futures_contract(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_contract_order_book_futures(client):
    res = client.get_contract_order_book(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_contract_kline_futures(client):
    res = client.get_contract_kline(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_contract_list_tickers_futures(client):
    res = client.get_contract_list_tickers(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_futures_funding_rate_history(client):
    res = client.get_futures_funding_rate_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_futures_contract_stats(client):
    res = client.get_futures_contract_stats(product_symbol="BTC-USDT-SWAP")
    assert res is not None


def test_get_all_delivery_contracts(client):
    res = client.get_all_delivery_contracts()
    assert res is not None


def test_get_contract_order_book_delivery(client):
    res = client.get_contract_order_book(
        product_symbol=_delivery_product_symbol(client),
        path="delivery",
    )
    assert res is not None


def test_get_contract_kline_delivery(client):
    res = client.get_contract_kline(
        product_symbol=_delivery_product_symbol(client),
        path="delivery",
    )
    assert res is not None


def test_get_contract_list_tickers_delivery(client):
    res = client.get_contract_list_tickers(
        product_symbol=_delivery_product_symbol(client),
        path="delivery",
    )
    assert res is not None


def test_get_spot_all_currency_pairs(client):
    res = client.get_spot_all_currency_pairs()
    assert res is not None


def test_get_spot_order_book(client):
    res = client.get_spot_order_book(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_spot_kline(client):
    res = client.get_spot_kline(product_symbol="BTC-USDT-SPOT")
    assert res is not None


def test_get_spot_list_tickers(client):
    res = client.get_spot_list_tickers(product_symbol="BTC-USDT-SPOT")
    assert res is not None
