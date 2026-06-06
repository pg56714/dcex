from dcex.hyperliquid.client import Client
import pytest


@pytest.fixture
def client():
    return Client()


def test_get_meta(client):
    res = client.get_meta()
    assert res is not None


def test_get_spot_meta(client):
    res = client.get_spot_meta()
    assert res is not None


def test_get_meta_and_asset_ctxs(client):
    res = client.get_meta_and_asset_ctxs()
    assert res is not None


def test_get_spot_meta_and_asset_ctxs(client):
    res = client.get_spot_meta_and_asset_ctxs()
    assert res is not None


def test_get_l2book(client):
    res = client.get_l2book(product_symbol="BTC-USD-SWAP")
    assert res is not None


def test_get_candle_snapshot(client):
    res = client.get_candle_snapshot(
        product_symbol="BTC-USD-SWAP",
        interval="1m",
        startTime=1696128000000,
    )
    assert res is not None


def test_get_funding_rate_history(client):
    res = client.get_funding_rate_history(
        product_symbol="BTC-USD-SWAP",
        startTime=1696128000000,
    )
    assert res is not None
