import pytest
import pytest_asyncio
from dcex.async_support.hyperliquid.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client() as client_instance:
        yield client_instance


@pytest.mark.asyncio
async def test_get_meta(client):
    res = await client.get_meta()
    assert res is not None

@pytest.mark.asyncio
async def test_get_spot_meta(client):
    res = await client.get_spot_meta()
    assert res is not None


@pytest.mark.asyncio
async def test_get_meta_and_asset_ctxs(client):
    res = await client.get_meta_and_asset_ctxs()
    assert res is not None


@pytest.mark.asyncio
async def test_get_spot_meta_and_asset_ctxs(client):
    res = await client.get_spot_meta_and_asset_ctxs()
    assert res is not None


@pytest.mark.asyncio
async def test_get_l2book(client):
    res = await client.get_l2book(product_symbol="FLASK-USDC-SPOT")
    assert res is not None

@pytest.mark.asyncio
async def test_get_candle_snapshot(client):
    res = await client.get_candle_snapshot(
            product_symbol="BTC-USD-SWAP",
            interval="1m",
            startTime=1696128000000,
        )
    assert res is not None
