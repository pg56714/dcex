# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest

from dcex.lighter.client import Client


@pytest.fixture
def client():
    client_instance = Client(preload_product_table=False)
    try:
        yield client_instance
    finally:
        client_instance.close()


def _active_perp_market_id(client: Client) -> int:
    res = client.get_order_book_details()
    markets = res.get("order_book_details", [])
    active = next(market for market in markets if market.get("status") == "active")
    return int(active["market_id"])


def _assert_response(res) -> None:
    assert isinstance(res, dict)
    assert res.get("code", 200) == 200


def test_get_info(client):
    res = client.get_info()
    assert isinstance(res, dict)


def test_get_status(client):
    _assert_response(client.get_status())


def test_get_announcement(client):
    _assert_response(client.get_announcement())


def test_get_order_book_details(client):
    res = client.get_order_book_details()
    assert res["code"] == 200
    assert res["order_book_details"]
    assert res["spot_order_book_details"]


def test_get_order_books(client):
    market_id = _active_perp_market_id(client)
    res = client.get_order_books(market_id=market_id)
    assert res["code"] == 200
    assert res["order_books"][0]["market_id"] == market_id


def test_get_order_book_orders(client):
    market_id = _active_perp_market_id(client)
    res = client.get_order_book_orders(market_id=market_id, limit=5)
    assert res["code"] == 200
    assert res["asks"]
    assert res["bids"]


def test_get_recent_trades(client):
    market_id = _active_perp_market_id(client)
    res = client.get_recent_trades(market_id=market_id, limit=5)
    assert res["code"] == 200
    assert res["trades"]


def test_get_candles(client):
    market_id = _active_perp_market_id(client)
    now = int(time.time())
    res = client.get_candles(
        market_id=market_id,
        resolution="1m",
        start_timestamp=now - 3600,
        end_timestamp=now,
        count_back=5,
    )
    assert res["code"] == 200
    assert res["c"]


def test_get_funding_rates(client):
    res = client.get_funding_rates()
    assert res["code"] == 200
    assert res["funding_rates"]


def test_get_fundings(client):
    market_id = _active_perp_market_id(client)
    now = int(time.time())
    res = client.get_fundings(
        market_id=market_id,
        resolution="1h",
        start_timestamp=now - 86400,
        end_timestamp=now,
        count_back=5,
    )
    assert res["code"] == 200
    assert res["fundings"]


def test_get_exchange_stats(client):
    res = client.get_exchange_stats()
    assert res["code"] == 200
    assert res["order_book_stats"]


def test_get_execute_stats(client):
    _assert_response(client.get_execute_stats(period="d"))


def test_get_exchange_metrics(client):
    _assert_response(client.get_exchange_metrics(period="w", kind="volume"))


def test_get_asset_details(client):
    res = client.get_asset_details()
    assert res["code"] == 200
    assert res["asset_details"]


def test_get_bridge_and_chain_info(client):
    _assert_response(client.get_deposit_networks())
    _assert_response(client.get_fastbridge_info())
    _assert_response(client.get_layer1_basic_info())
    _assert_response(client.get_withdrawal_delay())


def test_get_lease_options(client):
    _assert_response(client.get_lease_options())


def test_get_system_config(client):
    res = client.get_system_config()
    assert res["code"] == 200
    assert "liquidity_pool_index" in res


def test_get_token_list(client):
    _assert_response(client.get_token_list())
