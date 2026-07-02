# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time

import pytest
from dotenv import load_dotenv

from dcex.bitget.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

pytestmark = pytest.mark.private


@pytest.fixture
def client():
    client_instance = Client(
        api_key=BITGET_API_KEY,
        api_secret=BITGET_API_SECRET,
        passphrase=BITGET_PASSPHRASE,
    )
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_ok(response) -> dict:
    assert isinstance(response, dict)
    assert response["code"] == "00000", response
    assert "data" in response
    return response


def _is_uta(client) -> bool:
    try:
        data = _assert_ok(client.get_uta_account_info()).get("data", {})
    except FailedRequestError:
        return False
    permissions = data.get("permissions", []) if isinstance(data, dict) else []
    return "uta_trade" in permissions or "uta_mgt" in permissions


def _assert_uta_account_read_endpoints(client) -> None:
    _assert_ok(client.get_uta_account_info())
    _assert_ok(client.get_uta_account_assets())


def _assert_uta_trade_read_endpoints(client) -> None:
    _assert_ok(client.get_uta_open_orders("SPOT", "BTC-USDT-SPOT", limit=20))
    _assert_ok(client.get_uta_history_orders("SPOT", "BTC-USDT-SPOT", limit=20))
    _assert_ok(client.get_uta_fills("SPOT", limit=20))
    _assert_ok(client.get_uta_open_orders("USDT-FUTURES", "BTC-USDT-SWAP", limit=20))
    _assert_ok(client.get_uta_history_orders("USDT-FUTURES", "BTC-USDT-SWAP", limit=20))
    _assert_ok(client.get_uta_fills("USDT-FUTURES", limit=20))
    _assert_ok(client.get_uta_positions("USDT-FUTURES", "BTC-USDT-SWAP"))


def test_common_account_read_endpoints(client):
    if _is_uta(client):
        _assert_uta_account_read_endpoints(client)
        return
    _assert_ok(client.get_all_account_balance())
    _assert_ok(client.get_funding_assets(coin="USDT"))


def test_spot_account_read_endpoints(client):
    end_time = int(time.time() * 1000)
    start_time = end_time - 7 * 24 * 60 * 60 * 1000

    if _is_uta(client):
        _assert_uta_account_read_endpoints(client)
        _assert_ok(client.get_uta_open_orders("SPOT", "BTC-USDT-SPOT", limit=20))
        _assert_ok(client.get_uta_history_orders("SPOT", "BTC-USDT-SPOT", limit=20))
        return

    _assert_ok(client.get_spot_account_info())
    _assert_ok(client.get_spot_account_assets(coin="USDT"))
    _assert_ok(client.get_spot_account_bills(coin="USDT", limit=20))
    _assert_ok(client.get_transferable_coins(fromType="spot", toType="usdt_futures"))
    _assert_ok(client.get_transfer_records(coin="USDT", limit=20))
    _assert_ok(
        client.get_deposit_records(
            coin="USDT",
            startTime=start_time,
            endTime=end_time,
            limit=20,
        )
    )


def test_futures_account_read_endpoints(client):
    if _is_uta(client):
        _assert_uta_account_read_endpoints(client)
        _assert_ok(client.get_uta_positions("USDT-FUTURES", "BTC-USDT-SWAP"))
        return

    _assert_ok(client.get_futures_accounts())
    _assert_ok(client.get_futures_account(product_symbol="BTC-USDT-SWAP"))
    _assert_ok(client.get_futures_account_bills(limit=20))
    _assert_ok(client.get_futures_positions())
    _assert_ok(client.get_futures_position(product_symbol="BTC-USDT-SWAP"))


def test_private_trade_read_endpoints(client):
    if _is_uta(client):
        _assert_uta_trade_read_endpoints(client)
        return

    _assert_ok(client.get_spot_open_orders(product_symbol="BTC-USDT-SPOT", limit=20))
    _assert_ok(client.get_spot_history_orders(product_symbol="BTC-USDT-SPOT", limit=20))
    _assert_ok(client.get_spot_fills(product_symbol="BTC-USDT-SPOT", limit=20))
    _assert_ok(client.get_futures_open_orders(product_symbol="BTC-USDT-SWAP", limit=20))
    _assert_ok(client.get_futures_history_orders(product_symbol="BTC-USDT-SWAP", limit=20))
    _assert_ok(client.get_futures_fills(product_symbol="BTC-USDT-SWAP", limit=20))
