# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.bybit.client import Client

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")


@pytest.fixture
def client():
    return Client(
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    )


@pytest.mark.private
def test_rfq_read_endpoints(client):
    assert client.get_rfq_public_trades(limit=1) is not None
    assert client.get_rfq_config() is not None
    assert client.get_realtime_rfqs() is not None
    assert client.get_rfqs(limit=1) is not None
    assert client.get_rfq_details(limit=1) is not None
    assert client.get_realtime_rfq_quotes() is not None
    assert client.get_rfq_quotes(limit=1) is not None
    assert client.get_rfq_trade_history(limit=1) is not None
