# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bybit.client import Client
from dcex.utils.errors import FailedRequestError

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
async def test_get_wallet_balance(client):
    res = await client.get_wallet_balance()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_transferable_amount(client):
    res = await client.get_transferable_amount(coins=["BTC", "ETH"])
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_borrow_history(client):
    res = await client.get_borrow_history()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_collateral_info(client):
    res = await client.get_collateral_info()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_spot_fee_rates(client):
    res = await client.get_spot_fee_rates()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_account_info(client):
    res = await client.get_account_info()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_transaction_log(client):
    res = await client.get_transaction_log()
    assert res is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_margin_read_endpoints(client):
    assert await client.get_margin_max_borrowable("USDT") is not None
    assert await client.get_margin_position_tiers("USDT") is not None
    assert await client.get_margin_coin_state("USDT") is not None
    assert await client.get_margin_repayment_available_amount("USDT") is not None
    assert await client.get_margin_auto_repay_mode("USDT") is not None
    assert await client.get_fixed_borrow_quote("USDT", limit=1) is not None
    assert await client.get_fixed_borrow_orders(orderCurrency="USDT", limit=1) is not None
    assert await client.get_fixed_borrow_contracts(orderCurrency="USDT", limit=1) is not None
    assert await client.get_margin_liability("USDT") is not None
    assert await client.get_flexible_borrow_inventory("USDT") is not None


@pytest.mark.asyncio
@pytest.mark.private
async def test_earn_read_endpoints(client):
    assert await client.get_earn_products("FlexibleSaving", coin="USDT") is not None
    try:
        assert await client.get_earn_positions("FlexibleSaving", coin="USDT") is not None
        assert await client.get_earn_order_history("FlexibleSaving", limit=1) is not None
        assert await client.get_earn_yield_history("FlexibleSaving", limit=1) is not None
        assert await client.get_earn_hourly_yield_history(limit=1) is not None
    except FailedRequestError as exc:
        if "10005" in str(exc) and "Permission denied" in str(exc):
            pytest.skip("BYBIT_API_KEY does not have the Earn permission enabled.")
        raise
