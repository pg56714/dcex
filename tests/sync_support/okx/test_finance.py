# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os

import pytest
from dotenv import load_dotenv

from dcex.okx.client import Client

load_dotenv()

pytestmark = pytest.mark.private


@pytest.fixture
def client():
    return Client(
        api_key=os.getenv("OKX_API_KEY"),
        api_secret=os.getenv("OKX_API_SECRET"),
        passphrase=os.getenv("OKX_PASSPHRASE"),
    )


def _assert_ok(response):
    assert response["code"] in ("0", 0), response
    assert "data" in response
    return response


def test_savings_read_endpoints(client):
    _assert_ok(client.get_public_borrow_info("USDT"))
    _assert_ok(client.get_public_borrow_history("USDT", limit=20))
    _assert_ok(client.get_saving_balance("USDT"))
    _assert_ok(client.get_savings_lending_history("USDT", limit=20))


def test_onchain_earn_read_endpoints(client):
    _assert_ok(client.get_staking_offers())
    _assert_ok(client.get_active_staking_orders())
    _assert_ok(client.get_staking_order_history(limit=20))


def test_native_staking_read_endpoints(client):
    _assert_ok(client.get_eth_staking_product_info())
    _assert_ok(client.get_eth_staking_balance())
    _assert_ok(client.get_eth_staking_history(limit=20))
    _assert_ok(client.get_eth_staking_apy_history(7))
    _assert_ok(client.get_sol_staking_product_info())
    _assert_ok(client.get_sol_staking_balance())
    _assert_ok(client.get_sol_staking_history(limit=20))
    _assert_ok(client.get_sol_staking_apy_history(7))


def test_flexible_loan_read_endpoints(client):
    _assert_ok(client.get_flexible_loan_borrow_currencies())
    _assert_ok(client.get_flexible_loan_collateral_assets())
    _assert_ok(client.get_flexible_loan_max_collateral_redeem("BTC"))
    _assert_ok(client.get_flexible_loan_info())
    _assert_ok(client.get_flexible_loan_history(limit=20))
    _assert_ok(client.get_flexible_loan_interest_accrued(limit=20))
    _assert_ok(client.get_flexible_loan_emode_info())


def test_dual_investment_read_endpoints(client):
    currency_pairs = _assert_ok(client.get_dual_investment_currency_pairs())
    pair = currency_pairs["data"][0]
    _assert_ok(
        client.get_dual_investment_products(
            pair["baseCcy"], quoteCcy=pair["quoteCcy"], optType=pair["optType"]
        )
    )
    _assert_ok(client.get_dual_investment_order_history(limit=20))


def test_okusd_read_endpoints(client):
    _assert_ok(client.get_okusd_limits())
    _assert_ok(client.get_okusd_account())
    _assert_ok(client.get_okusd_rate_history(limit=20))
    _assert_ok(client.get_okusd_subscribe_history(limit=20))
    _assert_ok(client.get_okusd_redeem_history(limit=20))
    _assert_ok(client.get_okusd_rewards_history(limit=20))
