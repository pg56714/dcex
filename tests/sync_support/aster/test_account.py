# ruff: noqa: ANN001, ANN201, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.aster.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

ASTER_USER_ADDRESS = os.getenv("ASTER_USER_ADDRESS")
ASTER_SIGNER_ADDRESS = os.getenv("ASTER_SIGNER_ADDRESS")
ASTER_PRIVATE_KEY = os.getenv("ASTER_PRIVATE_KEY")

pytestmark = pytest.mark.private


@pytest.fixture
def client():
    client_instance = Client(
        user_address=ASTER_USER_ADDRESS,
        signer_address=ASTER_SIGNER_ADDRESS,
        private_key=ASTER_PRIVATE_KEY,
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


def test_spot_account_read_endpoints(client):
    account = _assert_response(client.get_spot_account())
    assert isinstance(account, dict)
    assert "balances" in account
    _assert_response(client.get_spot_transaction_history(limit=20))
    _assert_response(client.get_spot_commission_rate("BTCUSDT"))
    _assert_response(client.get_spot_open_orders())
    _assert_response(client.get_spot_all_orders("BTCUSDT", limit=20))
    _assert_response(client.get_spot_user_trades("BTCUSDT", limit=20))


def test_futures_account_read_endpoints(client):
    _assert_response(client.get_futures_balance())
    _assert_response(client.get_futures_account())
    _assert_response(client.get_futures_position_mode())
    _assert_response(client.get_futures_stp_mode())
    _assert_response(client.get_futures_multi_assets_mode())
    _assert_response(client.get_futures_position_risk())
    _assert_response(client.get_futures_position_margin_history("BTCUSDT", limit=20))
    _assert_response(client.get_futures_user_trades("BTCUSDT", limit=20))
    _assert_response(client.get_futures_income(limit=20))
    _assert_response(client.get_futures_leverage_bracket("BTCUSDT"))
    _assert_response(client.get_futures_adl_quantile())
    _assert_response(client.get_futures_force_orders(limit=20))
    _assert_response(client.get_futures_commission_rate("BTCUSDT"))
    _assert_response(client.get_futures_mmp("BTCUSDT"))


def test_futures_trade_read_endpoints(client):
    _assert_response(client.get_futures_open_orders())
    _assert_response(client.get_futures_all_orders("BTCUSDT", limit=20))


@pytest.mark.parametrize(
    "call",
    [
        lambda client: client.get_futures_strategy_open_order(
            strategyType="OTO",
            clientStrategyId="dcex-missing-strategy",
        ),
        lambda client: client.get_futures_strategy_history_order(
            strategyType="OTO",
            clientStrategyId="dcex-missing-strategy",
            limit=20,
        ),
    ],
)
def test_missing_strategy_query_returns_documented_error(client, call):
    with pytest.raises(FailedRequestError, match="Order does not exist"):
        call(client)


def test_spot_listen_key_lifecycle(client):
    created = _assert_response(client.create_spot_listen_key())
    assert isinstance(created, dict)
    listen_key = str(created["listenKey"])
    _assert_response(client.keep_alive_spot_listen_key(listen_key))
    _assert_response(client.close_spot_listen_key(listen_key))


def test_futures_listen_key_lifecycle(client):
    created = _assert_response(client.create_futures_listen_key())
    assert isinstance(created, dict)
    assert created.get("listenKey")
    _assert_response(client.keep_alive_futures_listen_key())
    _assert_response(client.close_futures_listen_key())
