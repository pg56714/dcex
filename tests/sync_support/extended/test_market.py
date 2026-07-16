# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest

from dcex.extended.client import Client


@pytest.fixture
def client():
    client_instance = Client(preload_product_table=False, timeout=20)
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_response(response: object) -> dict | list:
    assert isinstance(response, dict | list)
    return response


def test_public_reference_data(client):
    _assert_response(client.get_markets())
    _assert_response(client.get_assets())
    _assert_response(client.get_asset_index_price("BTC"))
    _assert_response(client.get_market_statistics("BTC-USD"))


def test_public_market_data(client):
    _assert_response(client.get_order_book("BTC-USD"))
    _assert_response(client.get_trades("BTC-USD"))
    _assert_response(
        client.get_candles(
            market="BTC-USD",
            interval="PT1M",
            limit=5,
        )
    )


def test_public_funding_and_open_interest(client):
    end_time = int(time.time() * 1000)
    start_time = end_time - 3 * 24 * 60 * 60 * 1000
    _assert_response(
        client.get_funding(
            market="BTC-USD",
            startTime=start_time,
            endTime=end_time,
            limit=5,
        )
    )
    _assert_response(
        client.get_open_interest(
            market="BTC-USD",
            interval="PT1H",
            startTime=start_time,
            endTime=end_time,
            limit=5,
        )
    )
