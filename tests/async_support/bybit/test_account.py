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


@pytest.mark.asyncio
async def test_advanced_earn_public_products_and_quotes(client):
    categories = ("DualAssets", "SmartLeverage", "DoubleWin", "DiscountBuy")
    for category in categories:
        products = await client.get_advanced_earn_products(category)
        assert products["retCode"] == 0
        product = products["result"]["list"][0]
        quote = await client.get_advanced_earn_product_quote(category, product["productId"])
        assert quote["retCode"] == 0


@pytest.mark.asyncio
@pytest.mark.private
async def test_advanced_earn_private_read_endpoints(client):
    categories = ("DualAssets", "SmartLeverage", "DoubleWin", "DiscountBuy")
    for category in categories:
        try:
            assert await client.get_advanced_earn_positions(category, limit=1) is not None
            assert await client.get_advanced_earn_orders(category, limit=1) is not None
        except FailedRequestError as exc:
            if "10005" in str(exc) and "Permission denied" in str(exc):
                pytest.skip("BYBIT_API_KEY does not have the Earn permission enabled.")
            raise


@pytest.mark.asyncio
async def test_liquidity_mining_public_products(client):
    products = await client.get_liquidity_mining_products()
    assert products["retCode"] == 0
    assert "products" in products["result"]


@pytest.mark.asyncio
@pytest.mark.private
async def test_liquidity_mining_private_read_endpoints(client):
    try:
        assert await client.get_liquidity_mining_positions() is not None
        assert await client.get_liquidity_mining_orders(limit=1) is not None
        assert await client.get_liquidity_mining_yield_records(limit=1) is not None
        assert await client.get_liquidity_mining_liquidation_records(limit=1) is not None
    except FailedRequestError as exc:
        if "10005" in str(exc) and "Permission denied" in str(exc):
            pytest.skip("BYBIT_API_KEY does not have the Earn permission enabled.")
        raise


@pytest.mark.asyncio
async def test_fixed_earn_public_products(client):
    products = await client.get_fixed_earn_products(coin="USDT")
    assert products["retCode"] == 0
    assert "list" in products["result"]


@pytest.mark.asyncio
@pytest.mark.private
async def test_fixed_earn_private_read_endpoints(client):
    try:
        assert await client.get_fixed_earn_positions() is not None
        assert await client.get_fixed_earn_orders(limit=1) is not None
    except FailedRequestError as exc:
        if "10005" in str(exc) and "Permission denied" in str(exc):
            pytest.skip("BYBIT_API_KEY does not have the Earn permission enabled.")
        raise


@pytest.mark.asyncio
async def test_hold_to_earn_public_products(client):
    products = await client.get_hold_to_earn_products()
    assert products["retCode"] == 0
    assert "products" in products["result"]


@pytest.mark.asyncio
@pytest.mark.private
async def test_hold_to_earn_private_yield(client):
    try:
        assert await client.get_hold_to_earn_yield_history(limit=1) is not None
    except FailedRequestError as exc:
        if "10005" in str(exc) and "Permission denied" in str(exc):
            pytest.skip("BYBIT_API_KEY does not have the Earn permission enabled.")
        raise


@pytest.mark.asyncio
async def test_byusdt_public_product_and_apr(client):
    assert (await client.get_byusdt_product())["retCode"] == 0
    assert (await client.get_byusdt_apr_history(1))["retCode"] == 0


@pytest.mark.asyncio
@pytest.mark.private
async def test_byusdt_private_read_endpoints(client):
    try:
        assert await client.get_byusdt_position() is not None
        assert await client.get_byusdt_orders(limit=1) is not None
        assert await client.get_byusdt_daily_yield(limit=1) is not None
        assert await client.get_byusdt_hourly_yield(limit=1) is not None
    except FailedRequestError as exc:
        if "10005" in str(exc) and "Permission denied" in str(exc):
            pytest.skip("BYBIT_API_KEY does not have the Earn permission enabled.")
        raise


@pytest.mark.asyncio
async def test_rwa_earn_public_products_and_nav(client):
    products = await client.get_rwa_earn_products()
    assert products["retCode"] == 0
    assert "list" in products["result"]
    if products["result"]["list"]:
        product_id = products["result"]["list"][0]["productId"]
        chart = await client.get_rwa_earn_nav_chart(product_id)
        assert chart["retCode"] == 0


@pytest.mark.asyncio
@pytest.mark.private
async def test_rwa_earn_private_read_endpoints(client):
    try:
        assert await client.get_rwa_earn_positions() is not None
        assert await client.get_rwa_earn_orders(limit=1) is not None
    except FailedRequestError as exc:
        if "10005" in str(exc) and "Permission denied" in str(exc):
            pytest.skip("BYBIT_API_KEY does not have the Earn permission enabled.")
        raise


@pytest.mark.asyncio
async def test_earn_public_apr_history(client):
    products = await client.get_earn_products("FlexibleSaving", coin="USDT")
    assert products["retCode"] == 0
    product_id = str(products["result"]["list"][0]["productId"])
    history = await client.get_earn_apr_history("FlexibleSaving", product_id)
    assert history["retCode"] == 0


@pytest.mark.asyncio
@pytest.mark.private
async def test_earn_coupon_list(client):
    try:
        assert await client.get_earn_coupons("FlexibleSaving") is not None
        assert await client.get_earn_coupons("DualAssets") is not None
    except FailedRequestError as exc:
        if "10005" in str(exc) and "Permission denied" in str(exc):
            pytest.skip("BYBIT_API_KEY does not have the Earn permission enabled.")
        raise


@pytest.mark.asyncio
async def test_launchpool_public_projects(client):
    projects = await client.get_launchpool_projects(1)
    assert projects["retCode"] == 0
    assert "list" in projects["result"]


@pytest.mark.asyncio
@pytest.mark.private
async def test_launchpool_private_read_endpoints(client):
    try:
        assert await client.get_launchpool_current_staking() is not None
        assert await client.get_launchpool_activity_log(pageSize=1) is not None
        assert await client.get_launchpool_history(pageSize=1) is not None
    except FailedRequestError as exc:
        if "10005" in str(exc) and "Permission denied" in str(exc):
            pytest.skip("BYBIT_API_KEY lacks permission for Launchpool queries.")
        raise
