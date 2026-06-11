# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.backpack.client import Client

load_dotenv()

BACKPACK_API_KEY = os.getenv("BACKPACK_API_KEY")
BACKPACK_API_SECRET = os.getenv("BACKPACK_API_SECRET")

pytestmark = pytest.mark.private


@pytest.fixture
def client():
    client_instance = Client(
        api_key=BACKPACK_API_KEY,
        api_secret=BACKPACK_API_SECRET,
        preload_product_table=False,
        timeout=20,
    )
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_response(response: object) -> dict | list:
    assert isinstance(response, dict | list)
    return response


def test_account_and_capital_read_endpoints(client):
    _assert_response(client.get_account())
    balances = _assert_response(client.get_balances())
    assert isinstance(balances, dict)
    _assert_response(client.get_private_collateral())
    _assert_response(client.get_deposits(limit=20))
    _assert_response(client.get_deposit_address(blockchain="Solana"))
    _assert_response(client.get_withdrawals(limit=20))
    _assert_response(client.get_dust_conversion_history(limit=20))
    _assert_response(client.get_settlement_history(limit=20))


def test_account_limit_read_endpoints(client):
    _assert_response(client.get_max_borrow_quantity(symbol="USDC"))
    _assert_response(client.get_max_order_quantity(symbol="SOL_USDC", side="Bid"))
    _assert_response(client.get_max_withdrawal_quantity(symbol="USDC"))


def test_borrow_lend_read_endpoints(client):
    _assert_response(client.get_borrow_lend_positions())
    _assert_response(client.get_borrow_history(limit=20))
    _assert_response(client.get_interest_history(limit=20))
    _assert_response(client.get_borrow_position_history(limit=20))


def test_trade_and_position_read_endpoints(client):
    _assert_response(client.get_open_orders())
    _assert_response(client.get_fill_history(limit=20))
    _assert_response(client.get_order_history(limit=20))
    _assert_response(client.get_open_positions())
    _assert_response(client.get_funding_payments(limit=20))
    _assert_response(client.get_position_history(limit=20))
