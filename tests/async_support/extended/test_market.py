# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest
import pytest_asyncio

from dcex.async_support.extended.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client(preload_product_table=False, timeout=20) as client_instance:
        yield client_instance


def _assert_response(response: object) -> dict | list:
    assert isinstance(response, dict | list)
    return response


@pytest.mark.asyncio
async def test_public_reference_and_market_data(client):
    _assert_response(await client.get_markets())
    _assert_response(await client.get_assets())
    _assert_response(await client.get_asset_index_price("BTC"))
    _assert_response(await client.get_market_statistics("BTC-USD"))
    _assert_response(await client.get_order_book("BTC-USD"))
    _assert_response(await client.get_trades("BTC-USD"))
    _assert_response(
        await client.get_candles(
            market="BTC-USD",
            interval="PT1M",
            limit=5,
        )
    )


@pytest.mark.asyncio
async def test_public_funding_and_open_interest(client):
    end_time = int(time.time() * 1000)
    start_time = end_time - 3 * 24 * 60 * 60 * 1000
    _assert_response(
        await client.get_funding(
            market="BTC-USD",
            startTime=start_time,
            endTime=end_time,
            limit=5,
        )
    )
    _assert_response(
        await client.get_open_interest(
            market="BTC-USD",
            interval="PT1H",
            startTime=start_time,
            endTime=end_time,
            limit=5,
        )
    )
