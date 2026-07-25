# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest
from dotenv import load_dotenv

from dcex.extended.client import Client

load_dotenv()

pytestmark = pytest.mark.private


@pytest.fixture
def client():
    client_instance = Client(preload_product_table=False, timeout=20)
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_response(response: object) -> dict | list:
    assert isinstance(response, dict | list)
    return response


def test_account_read_endpoints(client):
    _assert_response(client.get_account_details())
    _assert_response(client.get_sub_accounts())
    _assert_response(client.get_balance())
    _assert_response(client.get_spot_balances())
    _assert_response(client.get_asset_operations(limit=20))


def test_position_and_trade_history_read_endpoints(client):
    _assert_response(client.get_positions())
    _assert_response(client.get_positions_history(limit=20))
    _assert_response(client.get_trades_history(limit=20))
    _assert_response(
        client.get_funding_payments(
            startTime=int(time.time() * 1000) - 30 * 24 * 60 * 60 * 1000, limit=20
        )
    )


def test_fees_and_account_configuration_read_endpoints(client):
    _assert_response(client.get_leverage())
    _assert_response(client.get_fees())
    _assert_response(client.get_rebates())
    _assert_response(client.get_bridge_config())


def test_order_read_endpoints(client):
    _assert_response(client.get_open_orders())
    _assert_response(client.get_orders_history(limit=20))
