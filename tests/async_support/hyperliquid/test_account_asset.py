# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.hyperliquid.client import Client

load_dotenv()

WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")

pytestmark = pytest.mark.private


@pytest_asyncio.fixture
async def client():
    async with Client(
        wallet_address=WALLET_ADDRESS,
        private_key=PRIVATE_KEY,
        preload_product_table=False,
    ) as client_instance:
        yield client_instance


async def _account_user(client):
    role = await client.user_role(user=WALLET_ADDRESS)
    if isinstance(role, dict) and role.get("role") == "agent":
        return role.get("data", {}).get("user", WALLET_ADDRESS)
    return WALLET_ADDRESS


@pytest.mark.asyncio
async def test_account_readonly_endpoints(client):
    user = await _account_user(client)

    assert await client.clearinghouse_state(user=user) is not None
    assert await client.spot_clearinghouse_state(user=user) is not None
    assert await client.open_orders(user=user) is not None
    assert await client.user_fills(user=user, aggregateByTime=True) is not None
    assert await client.user_rate_limit(user=user) is not None
    assert await client.order_status(user=user, oid=0) is not None
    assert await client.historical_orders(user=user) is not None
    assert await client.subaccounts(user=user) is not None
    assert await client.user_role(user=WALLET_ADDRESS) is not None
    assert await client.portfolio(user=user) is not None


@pytest.mark.asyncio
async def test_asset_readonly_endpoints(client):
    assert await client.user_vault_equities(user=await _account_user(client)) is not None
