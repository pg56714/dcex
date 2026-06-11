# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest

from dcex.backpack.client import Client


@pytest.fixture
def client():
    client_instance = Client(preload_product_table=False)
    try:
        yield client_instance
    finally:
        client_instance.close()


def _markets(client: Client) -> list[dict]:
    res = client.get_markets()
    assert isinstance(res, list)
    assert res
    return res


def _market_symbol(client: Client, market_type: str) -> str:
    market = next(
        market
        for market in _markets(client)
        if market.get("visible") is not False
        and market.get("orderBookState") == "Open"
        and market.get("marketType") == market_type
    )
    return str(market["symbol"])


def test_get_assets_and_collateral(client):
    assert isinstance(client.get_assets(), list)
    assert isinstance(client.get_collateral(), list)


def test_get_borrow_lend_public_data(client):
    assert isinstance(client.get_borrow_lend_markets(), list)
    assert isinstance(client.get_borrow_lend_market_history(interval="1d"), list)
    assert isinstance(client.get_borrow_lend_apy(), dict)


def test_get_market_metadata(client):
    spot_symbol = _market_symbol(client, "SPOT")
    assert isinstance(client.get_market(spot_symbol), dict)
    assert isinstance(client.get_order_book_depth(spot_symbol, limit=5), dict)
    assert isinstance(client.get_ticker(spot_symbol), dict)
    assert isinstance(client.get_tickers(), list)


def test_get_public_trades_and_klines(client):
    spot_symbol = _market_symbol(client, "SPOT")
    now = int(time.time())
    assert isinstance(
        client.get_klines(
            spot_symbol,
            interval="1m",
            startTime=now - 3600,
            endTime=now,
        ),
        list,
    )
    assert isinstance(client.get_recent_trades(spot_symbol, limit=5), list)
    assert isinstance(client.get_historical_trades(spot_symbol, limit=5), list)


def test_get_futures_market_data(client):
    perp_symbol = _market_symbol(client, "PERP")
    assert isinstance(client.get_mark_prices(perp_symbol), list)
    assert isinstance(client.get_open_interest(perp_symbol), list)
    assert isinstance(client.get_funding_rates(perp_symbol, limit=5), list)


def test_get_system_public_data(client):
    assert isinstance(client.get_status(), dict)
    assert client.ping()
    assert client.get_time()
    assert isinstance(client.get_wallets(), list)


def test_get_securities_public_data(client):
    assert isinstance(client.get_market_sessions(), list)
    assert isinstance(client.get_securities(), list)
