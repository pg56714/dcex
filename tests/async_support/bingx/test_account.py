# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bingx.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BINGX_API_KEY,
        api_secret=BINGX_API_SECRET,
    ) as client_instance:
        yield client_instance


def _fail_if_rate_limited(exc: FailedRequestError) -> None:
    message = str(exc)
    if "100410" in message or "endpoint trigger frequency limit" in message:
        pytest.fail("BingX temporarily rate-limited this endpoint.", pytrace=False)


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_swap_account_balance(client):
    res = await client.get_swap_account_balance()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_account_balance(client):
    res = await client.get_account_balance()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_account_balance(client):
    try:
        res = await client.get_spot_account_balance()
    except FailedRequestError as exc:
        _fail_if_rate_limited(exc)
        raise
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_fund_account_balance(client):
    res = await client.get_fund_account_balance(asset="USDT")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_all_account_balance(client):
    res = await client.get_all_account_balance()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_account_uid(client):
    res = await client.get_account_uid()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_api_key_info(client):
    uid = (await client.get_account_uid())["data"]["uid"]
    res = await client.get_api_key_info(uid=uid)
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_transferable_coins_to_spot(client):
    res = await client.get_transferable_coins(fromAccount="fund", toAccount="spot")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_transferable_coins_to_swap(client):
    res = await client.get_transferable_coins(fromAccount="fund", toAccount="USDTMPerp")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_asset_transfer_records(client):
    res = await client.get_asset_transfer_records(
        fromAccount="fund",
        toAccount="spot",
        pageSize=5,
    )
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_open_positions(client):
    res = await client.get_open_positions(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_fund_flow(client):
    res = await client.get_fund_flow(limit=5)
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_listen_key(client):
    res = await client.get_listen_key()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_keep_alive_listen_key(client):
    listen_key = await client.get_listen_key()
    res = await client.keep_alive_listen_key(listen_key)
    assert res is not None
