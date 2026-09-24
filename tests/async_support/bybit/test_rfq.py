# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bybit.client import Client

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    ) as client_instance:
        yield client_instance


@pytest.mark.asyncio
@pytest.mark.private
async def test_rfq_read_endpoints(client):
    assert await client.get_rfq_public_trades(limit=1) is not None
    assert await client.get_rfq_config() is not None
    assert await client.get_realtime_rfqs() is not None
    assert await client.get_rfqs(limit=1) is not None
    assert await client.get_rfq_details(limit=1) is not None
    assert await client.get_realtime_rfq_quotes() is not None
    assert await client.get_rfq_quotes(limit=1) is not None
    assert await client.get_rfq_trade_history(limit=1) is not None
