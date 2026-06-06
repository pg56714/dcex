# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.hyperliquid.client import Client

load_dotenv()

WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")

pytestmark = pytest.mark.private


@pytest.fixture
def client():
    return Client(
        wallet_address=WALLET_ADDRESS,
        private_key=PRIVATE_KEY,
        preload_product_table=False,
    )


def _account_user(client):
    role = client.user_role(user=WALLET_ADDRESS)
    if isinstance(role, dict) and role.get("role") == "agent":
        return role.get("data", {}).get("user", WALLET_ADDRESS)
    return WALLET_ADDRESS


def test_account_readonly_endpoints(client):
    user = _account_user(client)

    assert client.clearinghouse_state(user=user) is not None
    assert client.spot_clearinghouse_state(user=user) is not None
    assert client.open_orders(user=user) is not None
    assert client.user_fills(user=user, aggregateByTime=True) is not None
    assert client.user_rate_limit(user=user) is not None
    assert client.order_status(user=user, oid=0) is not None
    assert client.historical_orders(user=user) is not None
    assert client.subaccounts(user=user) is not None
    assert client.user_role(user=WALLET_ADDRESS) is not None
    assert client.portfolio(user=user) is not None


def test_asset_readonly_endpoints(client):
    assert client.user_vault_equities(user=_account_user(client)) is not None
