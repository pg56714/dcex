# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time

import pytest
from dotenv import load_dotenv

from dcex.mexc.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET")

pytestmark = pytest.mark.private


@pytest.fixture
def client():
    client_instance = Client(api_key=MEXC_API_KEY, api_secret=MEXC_API_SECRET, timeout=20)
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_response(response) -> object:
    assert response is not None
    return response


def _assert_contract_success(response) -> dict:
    assert isinstance(response, dict)
    assert response["success"] is True
    assert response["code"] == 0
    assert "data" in response
    return response


def _assert_contract_ok(response) -> dict:
    assert isinstance(response, dict)
    assert response["success"] is True
    assert response["code"] == 0
    return response


def _fail_if_invalid_symbol(exc: FailedRequestError) -> None:
    message = str(exc).lower()
    if "-1121" in message or "invalid symbol" in message:
        pytest.fail(f"MEXC endpoint rejected the live symbol: {exc}", pytrace=False)
    raise exc


def test_spot_account_read_endpoints(client):
    _assert_response(client.get_kyc_status())
    try:
        _assert_response(client.get_spot_self_symbols())
    except FailedRequestError as exc:
        _fail_if_invalid_symbol(exc)
    account = _assert_response(client.get_spot_account())
    assert "balances" in account
    mx_deduct = _assert_response(client.get_spot_mx_deduct_status())
    _assert_response(client.set_spot_mx_deduct(mx_deduct["data"]["mxDeductEnable"]))
    _assert_response(client.get_spot_symbol_commission("BTC-USDT-SPOT"))
    _assert_response(client.get_currency_info(coin="USDT"))
    _assert_response(client.get_deposit_history(coin="USDT", limit=10))
    _assert_response(client.get_withdraw_history(coin="USDT", limit=10))
    _assert_response(client.get_deposit_address(coin="USDT"))


def test_transfer_read_endpoints(client):
    _assert_response(
        client.get_user_universal_transfer_history(
            fromAccountType="SPOT",
            toAccountType="FUTURES",
            page=1,
            size=10,
        )
    )
    _assert_response(
        client.get_user_universal_transfer_history(
            fromAccountType="FUTURES",
            toAccountType="SPOT",
            page=1,
            size=10,
        )
    )
    _assert_response(client.get_internal_transfer_history(page=1, limit=10))
    _assert_contract_success(
        client.get_contract_transfer_records(currency="USDT", page_num=1, page_size=10)
    )


def test_contract_account_read_endpoints(client):
    _assert_contract_success(client.get_contract_assets())
    _assert_contract_success(client.get_contract_asset("USDT"))
    _assert_contract_success(
        client.get_contract_history_positions(
            product_symbol="BTC-USDT-SWAP",
            page_num=1,
            page_size=10,
        )
    )
    _assert_contract_success(client.get_contract_open_positions("BTC-USDT-SWAP"))
    _assert_contract_success(
        client.get_contract_funding_records(
            product_symbol="BTC-USDT-SWAP",
            page_num=1,
            page_size=10,
        )
    )
    _assert_contract_success(client.get_contract_risk_limits("BTC-USDT-SWAP"))
    _assert_contract_success(client.get_contract_trading_fee_rate("BTC-USDT-SWAP"))
    _assert_contract_success(client.get_contract_leverage("BTC-USDT-SWAP"))
    _assert_contract_ok(
        client.change_contract_leverage(
            leverage=50,
            openType=2,
            product_symbol="BTC-USDT-SWAP",
            positionType=1,
        )
    )
    _assert_contract_ok(
        client.change_contract_leverage(
            leverage=50,
            openType=2,
            product_symbol="BTC-USDT-SWAP",
            positionType=2,
        )
    )
    position_mode = _assert_contract_success(client.get_contract_position_mode())["data"]
    try:
        _assert_contract_ok(client.change_contract_position_mode(position_mode))
    except FailedRequestError as exc:
        assert "7001" in str(exc)


def test_private_trade_read_endpoints(client):
    end_time = int(time.time() * 1000)
    start_time = end_time - 86_400_000
    _assert_response(client.get_spot_open_orders("BTC-USDT-SPOT"))
    _assert_response(client.get_spot_all_orders("BTC-USDT-SPOT", limit=10))
    _assert_response(client.get_spot_my_trades("BTC-USDT-SPOT", limit=10))
    _assert_contract_success(
        client.get_contract_open_orders("BTC-USDT-SWAP", page_num=1, page_size=10)
    )
    _assert_contract_success(
        client.get_contract_history_orders("BTC-USDT-SWAP", page_num=1, page_size=10)
    )
    _assert_contract_success(
        client.get_contract_order_deals("BTC-USDT-SWAP", page_num=1, page_size=10)
    )
    _assert_contract_success(
        client.get_contract_plan_orders(
            start_time=start_time,
            end_time=end_time,
            product_symbol="BTC-USDT-SWAP",
            page_num=1,
            page_size=10,
        )
    )
    _assert_contract_success(
        client.get_contract_stop_orders("BTC-USDT-SWAP", page_num=1, page_size=10)
    )
