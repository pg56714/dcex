# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.okx.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")


def _fail_if_deposit_withdraw_status_unavailable(exc) -> None:
    message = str(exc)
    if "58214" in message:
        pytest.fail(
            "OKX deposit/withdraw status is unavailable during chain maintenance.",
            pytrace=False,
        )
    if "50011" in message or "Too many requests" in message:
        pytest.fail("OKX rate-limited the deposit/withdraw status endpoint.", pytrace=False)


@pytest_asyncio.fixture
async def client():
    import asyncio

    client_instance = Client(
        api_key=OKX_API_KEY,
        api_secret=OKX_API_SECRET,
        passphrase=OKX_PASSPHRASE,
    )
    await client_instance.async_init()
    yield client_instance
    await client_instance.close()
    # Give time for connections to fully close on Windows
    await asyncio.sleep(0.05)


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_currencies(client):
    res = await client.get_currencies()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_balances(client):
    res = await client.get_balances()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_asset_valuation(client):
    res = await client.get_asset_valuation()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_bills(client):
    res = await client.get_bills()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_deposit_address(client):
    res = await client.get_deposit_address(ccy="BTC")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_deposit_history(client):
    res = await client.get_deposit_history()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_deposit_withdraw_status(client):
    history = await client.get_deposit_history(ccy="USDT")
    deposit = next(
        (
            item
            for item in history.get("data", [])
            if isinstance(item, dict)
            and item.get("txId")
            and item.get("ccy")
            and item.get("to")
            and item.get("chain")
        ),
        None,
    )
    if deposit is None:
        pytest.fail("OKX account has no complete USDT deposit record to query.", pytrace=False)
    try:
        res = await client.get_deposit_withdraw_status(
            txId=deposit["txId"],
            ccy=deposit["ccy"],
            to=deposit["to"],
            chain=deposit["chain"],
        )
    except FailedRequestError as exc:
        _fail_if_deposit_withdraw_status_unavailable(exc)
        raise
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_exchange_list(client):
    res = await client.get_exchange_list()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_post_monthly_statement(client):
    res = await client.post_monthly_statement(month="Mar")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_monthly_statement(client):
    res = await client.get_monthly_statement(month="Mar")
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_convert_currencies(client):
    res = await client.get_convert_currencies()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_convert_history(client):
    res = await client.get_convert_history()
    assert res is not None
