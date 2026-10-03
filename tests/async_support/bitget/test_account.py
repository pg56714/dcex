# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bitget.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

pytestmark = pytest.mark.private


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BITGET_API_KEY,
        api_secret=BITGET_API_SECRET,
        passphrase=BITGET_PASSPHRASE,
    ) as client_instance:
        yield client_instance


def _assert_ok(response) -> dict:
    assert isinstance(response, dict)
    assert response["code"] == "00000", response
    assert "data" in response
    return response


async def _assert_crypto_loan_debts_or_empty(client) -> None:
    try:
        _assert_ok(await client.get_crypto_loan_debts())
    except FailedRequestError as exc:
        assert "[40054]" in exc.message and "is empty" in exc.message, exc


async def _assert_uta_account_read_endpoints(client) -> None:
    _assert_ok(await client.get_uta_account_info())
    _assert_ok(await client.get_uta_account_assets())


async def _assert_uta_trade_read_endpoints(client) -> None:
    _assert_ok(await client.get_uta_open_orders("SPOT", "BTC-USDT-SPOT", limit=20))
    _assert_ok(await client.get_uta_history_orders("SPOT", "BTC-USDT-SPOT", limit=20))
    _assert_ok(await client.get_uta_fills("SPOT", limit=20))
    _assert_ok(await client.get_uta_open_orders("USDT-FUTURES", "BTC-USDT-SWAP", limit=20))
    _assert_ok(await client.get_uta_history_orders("USDT-FUTURES", "BTC-USDT-SWAP", limit=20))
    _assert_ok(await client.get_uta_fills("USDT-FUTURES", limit=20))
    _assert_ok(await client.get_uta_positions("USDT-FUTURES", "BTC-USDT-SWAP"))


@pytest.mark.asyncio
async def test_common_account_read_endpoints(client):
    await _assert_uta_account_read_endpoints(client)


@pytest.mark.asyncio
async def test_spot_account_read_endpoints(client):
    await _assert_uta_account_read_endpoints(client)
    _assert_ok(await client.get_uta_open_orders("SPOT", "BTC-USDT-SPOT", limit=20))
    _assert_ok(await client.get_uta_history_orders("SPOT", "BTC-USDT-SPOT", limit=20))


@pytest.mark.asyncio
async def test_futures_account_read_endpoints(client):
    await _assert_uta_account_read_endpoints(client)
    _assert_ok(await client.get_uta_positions("USDT-FUTURES", "BTC-USDT-SWAP"))


@pytest.mark.asyncio
async def test_private_trade_read_endpoints(client):
    await _assert_uta_trade_read_endpoints(client)


@pytest.mark.asyncio
async def test_crypto_loan_read_endpoints(client):
    end_time = int(time.time() * 1000)
    start_time = end_time - 7 * 24 * 60 * 60 * 1000

    _assert_ok(await client.get_crypto_loan_coins())
    _assert_ok(await client.get_crypto_loan_ongoing())
    _assert_ok(await client.get_crypto_loan_borrow_history(str(start_time), str(end_time)))
    _assert_ok(await client.get_crypto_loan_repay_history(str(start_time), str(end_time)))
    _assert_ok(await client.get_crypto_loan_pledge_history(str(start_time), str(end_time)))
    _assert_ok(await client.get_crypto_loan_liquidations(str(start_time), str(end_time)))
    await _assert_crypto_loan_debts_or_empty(client)


@pytest.mark.asyncio
async def test_elite_earn_read_endpoints(client):
    products_response = _assert_ok(await client.get_elite_earn_products())
    _assert_ok(await client.get_elite_earn_assets())
    for record_type in ("subscribe", "redeem", "interest"):
        _assert_ok(await client.get_elite_earn_records(record_type, limit=20))

    products = products_response["data"]
    if isinstance(products, list) and products:
        product_id = products[0].get("productId")
        if product_id:
            _assert_ok(await client.get_elite_earn_subscription_info(product_id))
            _assert_ok(await client.get_elite_earn_redemption_info(product_id))
