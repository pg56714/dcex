"""
Offline route coverage for every Bybit sync and async endpoint wrapper.

Each case drives the public Python wrapper through the real native
``BybitHttpClient`` against a local HTTP server and asserts the HTTP verb,
the official V5 path, and whether the request was signed.
"""
# ruff: noqa: ANN401, D101, D103, N803

from __future__ import annotations

import asyncio
import json
import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

native = pytest.importorskip("dcex._native")

LINEAR = "BTC-USDT-SWAP"
SPOT = "BTC-USDT-SPOT"
BATCH = [{"symbol": "BTCUSDT", "side": "Buy", "orderType": "Limit", "qty": "1", "price": "1"}]
RFQ_LEGS = [{"category": "option", "symbol": "BTC-C", "side": "Buy", "qty": "1"}]


@dataclass(frozen=True)
class RouteCase:
    method_name: str
    verb: str
    path: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    signed: bool = True
    query: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)


def _get(
    name: str,
    path: str,
    *args: Any,
    signed: bool = True,
    query: dict[str, str] | None = None,
    **kwargs: Any,
) -> RouteCase:
    return RouteCase(name, "GET", path, args, kwargs, signed, query or {})


def _post(
    name: str,
    path: str,
    *args: Any,
    body: dict[str, Any] | None = None,
    **kwargs: Any,
) -> RouteCase:
    return RouteCase(name, "POST", path, args, kwargs, True, {}, body or {})


CASES: tuple[RouteCase, ...] = (
    _get("get_server_time", "/v5/market/time", signed=False),
    _get(
        "get_fixed_loan_supply_contract_info",
        "/v5/crypto-loan-fixed/supply-contract-info",
        supply_currency="USDT",
        query={"supplyCurrency": "USDT"},
    ),
    RouteCase(
        "get_spot_lever_token_reference",
        "GET",
        "/v5/spot-lever-token/reference",
        kwargs={"lt_coin": "BTC3L"},
        signed=False,
        query={"ltCoin": "BTC3L"},
    ),
    RouteCase(
        "get_spot_lever_token_order_record",
        "GET",
        "/v5/spot-lever-token/order-record",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "spot_lever_token_purchase",
        "POST",
        "/v5/spot-lever-token/purchase",
        kwargs={"lt_coin": "BTC3L", "lt_amount": "10"},
        signed=True,
        body={"ltCoin": "BTC3L", "ltAmount": "10"},
    ),
    RouteCase(
        "spot_lever_token_redeem",
        "POST",
        "/v5/spot-lever-token/redeem",
        kwargs={"lt_coin": "BTC3L", "quantity": "1"},
        signed=True,
        body={"ltCoin": "BTC3L", "quantity": "1"},
    ),
    RouteCase(
        "get_asset_withdraw_vasp_list",
        "GET",
        "/v5/asset/withdraw/vasp/list",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_asset_withdraw_query_address",
        "GET",
        "/v5/asset/withdraw/query-address",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_asset_withdraw_query_record",
        "GET",
        "/v5/asset/withdraw/query-record",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_borrowable_collateralisable_number",
        "GET",
        "/v5/crypto-loan/borrowable-collateralisable-number",
        kwargs={"loan_currency": "BTC", "collateral_currency": "USDT"},
        signed=True,
        query={"loanCurrency": "BTC", "collateralCurrency": "USDT"},
    ),
    RouteCase(
        "crypto_loan_adjust_ltv",
        "POST",
        "/v5/crypto-loan/adjust-ltv",
        kwargs={"order_id": "123", "amount": "1", "direction": "0"},
        signed=True,
        body={"orderId": "123", "amount": "1", "direction": "0"},
    ),
    RouteCase(
        "get_crypto_loan_collateral_data",
        "GET",
        "/v5/crypto-loan/collateral-data",
        kwargs={},
        signed=False,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_borrow_history",
        "GET",
        "/v5/crypto-loan/borrow-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_loanable_data",
        "GET",
        "/v5/crypto-loan/loanable-data",
        kwargs={},
        signed=False,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_adjustment_history",
        "GET",
        "/v5/crypto-loan/adjustment-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_max_collateral_amount",
        "GET",
        "/v5/crypto-loan/max-collateral-amount",
        kwargs={"order_id": "123"},
        signed=True,
        query={"orderId": "123"},
    ),
    RouteCase(
        "get_crypto_loan_repayment_history",
        "GET",
        "/v5/crypto-loan/repayment-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_repay",
        "POST",
        "/v5/crypto-loan/repay",
        kwargs={"order_id": "123", "amount": "1"},
        signed=True,
        body={"orderId": "123", "amount": "1"},
    ),
    RouteCase(
        "get_crypto_loan_ongoing_orders",
        "GET",
        "/v5/crypto-loan/ongoing-orders",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_spot_x_puzzle_project_list",
        "GET",
        "/v5/spot-x/puzzle/project/list",
        kwargs={"status": 1},
        signed=True,
        query={"status": "1"},
    ),
    RouteCase(
        "get_spot_x_token_splash_project_list",
        "GET",
        "/v5/spot-x/token-splash/project/list",
        kwargs={"status": 1},
        signed=True,
        query={"status": "1"},
    ),
    RouteCase(
        "get_spot_x_token_splash_user_activity_params",
        "GET",
        "/v5/spot-x/token-splash/user/activity-params",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_common_adjust_ltv",
        "POST",
        "/v5/crypto-loan-common/adjust-ltv",
        kwargs={"currency": "BTC", "amount": "1", "direction": "0"},
        signed=True,
        body={"currency": "BTC", "amount": "1", "direction": "0"},
    ),
    RouteCase(
        "get_crypto_loan_common_collateral_data",
        "GET",
        "/v5/crypto-loan-common/collateral-data",
        kwargs={},
        signed=False,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_common_position",
        "GET",
        "/v5/crypto-loan-common/position",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_fixed_available_inventory",
        "GET",
        "/v5/crypto-loan-fixed/available-inventory",
        kwargs={"currency": "BTC", "term": "7", "annual_rate": "0.02"},
        signed=True,
        query={"currency": "BTC", "term": "7", "annualRate": "0.02"},
    ),
    RouteCase(
        "get_crypto_loan_fixed_borrow_contract_info",
        "GET",
        "/v5/crypto-loan-fixed/borrow-contract-info",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_fixed_borrow_order_quote",
        "GET",
        "/v5/crypto-loan-fixed/borrow-order-quote",
        kwargs={"order_currency": "USDT", "order_by": "apy"},
        signed=False,
        query={"orderCurrency": "USDT", "orderBy": "apy"},
    ),
    RouteCase(
        "get_crypto_loan_fixed_borrow_order_info",
        "GET",
        "/v5/crypto-loan-fixed/borrow-order-info",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_fixed_borrow",
        "POST",
        "/v5/crypto-loan-fixed/borrow",
        kwargs={
            "order_currency": "USDT",
            "order_amount": "1",
            "annual_rate": "0.02",
            "term": "7",
            "collateral_list": [{"amount": "100", "currency": "USDT"}],
        },
        signed=True,
        body={
            "orderCurrency": "USDT",
            "orderAmount": "1",
            "annualRate": "0.02",
            "term": "7",
            "collateralList": [{"amount": "100", "currency": "USDT"}],
        },
    ),
    RouteCase(
        "crypto_loan_fixed_borrow_order_cancel",
        "POST",
        "/v5/crypto-loan-fixed/borrow-order-cancel",
        kwargs={"order_id": "123"},
        signed=True,
        body={"orderId": "123"},
    ),
    RouteCase(
        "crypto_loan_fixed_supply_order_cancel",
        "POST",
        "/v5/crypto-loan-fixed/supply-order-cancel",
        kwargs={"order_id": "123"},
        signed=True,
        body={"orderId": "123"},
    ),
    RouteCase(
        "get_crypto_loan_fixed_renew_info",
        "GET",
        "/v5/crypto-loan-fixed/renew-info",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_fixed_renew",
        "POST",
        "/v5/crypto-loan-fixed/renew",
        kwargs={"loan_id": "123", "collateral_list": [{"amount": "100", "currency": "USDT"}]},
        signed=True,
        body={"loanId": "123", "collateralList": [{"amount": "100", "currency": "USDT"}]},
    ),
    RouteCase(
        "crypto_loan_fixed_repay_collateral",
        "POST",
        "/v5/crypto-loan-fixed/repay-collateral",
        kwargs={"loan_currency": "BTC", "collateral_coin": "USDT", "amount": "1"},
        signed=True,
        body={"loanCurrency": "BTC", "collateralCoin": "USDT", "amount": "1"},
    ),
    RouteCase(
        "get_crypto_loan_fixed_repayment_history",
        "GET",
        "/v5/crypto-loan-fixed/repayment-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_fixed_fully_repay",
        "POST",
        "/v5/crypto-loan-fixed/fully-repay",
        kwargs={"loan_id": "123"},
        signed=True,
        body={"loanId": "123"},
    ),
    RouteCase(
        "get_crypto_loan_fixed_supply_order_quote",
        "GET",
        "/v5/crypto-loan-fixed/supply-order-quote",
        kwargs={"order_currency": "USDT", "order_by": "apy"},
        signed=False,
        query={"orderCurrency": "USDT", "orderBy": "apy"},
    ),
    RouteCase(
        "get_crypto_loan_fixed_supply_order_info",
        "GET",
        "/v5/crypto-loan-fixed/supply-order-info",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_fixed_supply",
        "POST",
        "/v5/crypto-loan-fixed/supply",
        kwargs={"order_currency": "USDT", "order_amount": "1", "annual_rate": "0.02", "term": "7"},
        signed=True,
        body={"orderCurrency": "USDT", "orderAmount": "1", "annualRate": "0.02", "term": "7"},
    ),
    RouteCase(
        "get_crypto_loan_flexible_available_inventory",
        "GET",
        "/v5/crypto-loan-flexible/available-inventory",
        kwargs={"currency": "BTC"},
        signed=True,
        query={"currency": "BTC"},
    ),
    RouteCase(
        "crypto_loan_flexible_borrow",
        "POST",
        "/v5/crypto-loan-flexible/borrow",
        kwargs={
            "loan_currency": "BTC",
            "loan_amount": "1",
            "collateral_list": [{"amount": "100", "currency": "USDT"}],
        },
        signed=True,
        body={
            "loanCurrency": "BTC",
            "loanAmount": "1",
            "collateralList": [{"amount": "100", "currency": "USDT"}],
        },
    ),
    RouteCase(
        "get_crypto_loan_flexible_borrow_history",
        "GET",
        "/v5/crypto-loan-flexible/borrow-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_flexible_repay_collateral",
        "POST",
        "/v5/crypto-loan-flexible/repay-collateral",
        kwargs={"loan_currency": "BTC", "collateral_coin": "USDT", "amount": "1"},
        signed=True,
        body={"loanCurrency": "BTC", "collateralCoin": "USDT", "amount": "1"},
    ),
    RouteCase(
        "get_crypto_loan_flexible_repayment_history",
        "GET",
        "/v5/crypto-loan-flexible/repayment-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_flexible_repay",
        "POST",
        "/v5/crypto-loan-flexible/repay",
        kwargs={"loan_currency": "BTC", "amount": "1"},
        signed=True,
        body={"loanCurrency": "BTC", "amount": "1"},
    ),
    RouteCase(
        "get_crypto_loan_flexible_ongoing_coin",
        "GET",
        "/v5/crypto-loan-flexible/ongoing-coin",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_common_loanable_data",
        "GET",
        "/v5/crypto-loan-common/loanable-data",
        kwargs={},
        signed=False,
        query={},
    ),
    RouteCase(
        "get_crypto_loan_common_adjustment_history",
        "GET",
        "/v5/crypto-loan-common/adjustment-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "crypto_loan_common_max_loan",
        "POST",
        "/v5/crypto-loan-common/max-loan",
        kwargs={"currency": "BTC"},
        signed=True,
        body={"currency": "BTC"},
    ),
    RouteCase(
        "get_crypto_loan_common_max_collateral_amount",
        "GET",
        "/v5/crypto-loan-common/max-collateral-amount",
        kwargs={"currency": "BTC"},
        signed=True,
        query={"currency": "BTC"},
    ),
    RouteCase(
        "get_all_api_rate_limits", "GET", "/v5/apilimit/query-all", kwargs={}, signed=True, query={}
    ),
    RouteCase(
        "get_api_rate_limit_cap", "GET", "/v5/apilimit/query-cap", kwargs={}, signed=True, query={}
    ),
    RouteCase(
        "get_api_rate_limits",
        "GET",
        "/v5/apilimit/query",
        kwargs={"uids": "2"},
        signed=True,
        query={"uids": "2"},
    ),
    RouteCase(
        "set_api_rate_limits",
        "POST",
        "/v5/apilimit/set",
        kwargs={"list": [{"uids": "2", "bizType": "DERIVATIVES", "rate": 10}]},
        signed=True,
        body={"list": [{"uids": "2", "bizType": "DERIVATIVES", "rate": 10}]},
    ),
    RouteCase(
        "submit_deposit_information",
        "POST",
        "/v5/asset/travel-rule/deposit/submit",
        kwargs={"deposit_id": 123, "questionnaire": '{"test":"fixture"}'},
        signed=True,
        body={"depositId": 123, "questionnaire": '{"test":"fixture"}'},
    ),
    RouteCase(
        "get_announcements",
        "GET",
        "/v5/announcements/index",
        kwargs={"locale": "en-US"},
        signed=False,
        query={"locale": "en-US"},
    ),
    RouteCase(
        "execute_small_balance_quote",
        "POST",
        "/v5/asset/covert/small-balance-execute",
        kwargs={"quote_id": "quote-1"},
        signed=True,
        body={"quoteId": "quote-1"},
    ),
    RouteCase(
        "get_small_balance_history",
        "GET",
        "/v5/asset/covert/small-balance-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "request_small_balance_quote",
        "POST",
        "/v5/asset/covert/get-quote",
        kwargs={
            "account_type": "eb_convert_uta",
            "from_coin_list": ["BTC", "ETH"],
            "to_coin": "USDC",
        },
        signed=True,
        body={"accountType": "eb_convert_uta", "fromCoinList": ["BTC", "ETH"], "toCoin": "USDC"},
    ),
    RouteCase(
        "get_small_balance_coins",
        "GET",
        "/v5/asset/covert/small-balance-list",
        kwargs={"account_type": "eb_convert_uta"},
        signed=True,
        query={"accountType": "eb_convert_uta"},
    ),
    RouteCase(
        "get_convert_coins",
        "GET",
        "/v5/asset/exchange/query-coin-list",
        kwargs={"account_type": "eb_convert_uta"},
        signed=True,
        query={"accountType": "eb_convert_uta"},
    ),
    RouteCase(
        "get_convert_history",
        "GET",
        "/v5/asset/exchange/query-convert-history",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_sub_account_deposit_address",
        "GET",
        "/v5/asset/deposit/query-sub-member-address",
        kwargs={"coin": "USDT", "chain_type": "ETH", "sub_member_id": "2"},
        signed=True,
        query={"coin": "USDT", "chainType": "ETH", "subMemberId": "2"},
    ),
    RouteCase(
        "get_exchange_order_records",
        "GET",
        "/v5/asset/exchange/order-record",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_fee_group_info",
        "GET",
        "/v5/market/fee-group-info",
        kwargs={"product_type": "contract"},
        signed=False,
        query={"productType": "contract"},
    ),
    RouteCase(
        "get_index_price_components",
        "GET",
        "/v5/market/index-price-components",
        kwargs={"index_name": "BTCUSDT"},
        signed=False,
        query={"indexName": "BTCUSDT"},
    ),
    RouteCase(
        "get_option_delivery_prices",
        "GET",
        "/v5/market/new-delivery-price",
        kwargs={"category": "option", "base_coin": "BTC"},
        signed=False,
        query={"category": "option", "baseCoin": "BTC"},
    ),
    RouteCase(
        "get_option_base_coins",
        "GET",
        "/v5/market/option-base-coins",
        kwargs={},
        signed=False,
        query={},
    ),
    RouteCase(
        "get_pre_upgrade_closed_pnl",
        "GET",
        "/v5/pre-upgrade/position/closed-pnl",
        kwargs={"category": "linear", "symbol": "BTCUSDT"},
        signed=True,
        query={"category": "linear", "symbol": "BTCUSDT"},
    ),
    RouteCase(
        "get_pre_upgrade_delivery_records",
        "GET",
        "/v5/pre-upgrade/asset/delivery-record",
        kwargs={"category": "option"},
        signed=True,
        query={"category": "option"},
    ),
    RouteCase(
        "get_pre_upgrade_executions",
        "GET",
        "/v5/pre-upgrade/execution/list",
        kwargs={"category": "linear"},
        signed=True,
        query={"category": "linear"},
    ),
    RouteCase(
        "get_pre_upgrade_order_history",
        "GET",
        "/v5/pre-upgrade/order/history",
        kwargs={"category": "linear"},
        signed=True,
        query={"category": "linear"},
    ),
    RouteCase(
        "get_pre_upgrade_settlement_records",
        "GET",
        "/v5/pre-upgrade/asset/settlement-record",
        kwargs={"category": "linear"},
        signed=True,
        query={"category": "linear"},
    ),
    RouteCase(
        "get_pre_upgrade_transaction_log",
        "GET",
        "/v5/pre-upgrade/account/transaction-log",
        kwargs={"category": "linear"},
        signed=True,
        query={"category": "linear"},
    ),
    RouteCase(
        "get_margin_currency_data",
        "GET",
        "/v5/spot-margin-trade/currency-data",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "create_sub_account_api_key",
        "POST",
        "/v5/user/create-sub-api",
        kwargs={"subuid": 2, "read_only": 1, "permissions": {"Spot": ["SpotTrade"]}},
        signed=True,
        body={"subuid": 2, "readOnly": 1, "permissions": {"Spot": ["SpotTrade"]}},
    ),
    RouteCase(
        "create_sub_account",
        "POST",
        "/v5/user/create-sub-member",
        kwargs={"username": "trader123", "member_type": 1},
        signed=True,
        body={"username": "trader123", "memberType": 1},
    ),
    RouteCase(
        "set_sub_account_frozen",
        "POST",
        "/v5/user/frozen-sub-member",
        kwargs={"subuid": 2, "frozen": 1},
        signed=True,
        body={"subuid": 2, "frozen": 1},
    ),
    RouteCase(
        "get_sub_account_api_keys",
        "GET",
        "/v5/user/sub-apikeys",
        kwargs={"sub_member_id": "2"},
        signed=True,
        query={"subMemberId": "2"},
    ),
    RouteCase(
        "modify_api_key",
        "POST",
        "/v5/user/update-api",
        kwargs={"confirm": True, "read_only": 1},
        signed=True,
        body={"readOnly": 1},
    ),
    RouteCase(
        "modify_sub_account_api_key",
        "POST",
        "/v5/user/update-sub-api",
        kwargs={},
        signed=True,
        body={},
    ),
    RouteCase(
        "get_sub_accounts_paginated", "GET", "/v5/user/submembers", kwargs={}, signed=True, query={}
    ),
    RouteCase(
        "delete_api_key",
        "POST",
        "/v5/user/delete-api",
        kwargs={"confirm": True},
        signed=True,
        body={},
    ),
    RouteCase(
        "delete_sub_account_api_key",
        "POST",
        "/v5/user/delete-sub-api",
        kwargs={},
        signed=True,
        body={},
    ),
    RouteCase(
        "delete_sub_account",
        "POST",
        "/v5/user/del-submember",
        kwargs={"sub_member_id": "2"},
        signed=True,
        body={"subMemberId": "2"},
    ),
    RouteCase(
        "sign_trading_agreement",
        "POST",
        "/v5/user/agreement",
        kwargs={"category_v2": 1, "agree": True},
        signed=True,
        body={"categoryV2": 1, "agree": True},
    ),
    RouteCase(
        "get_sub_accounts", "GET", "/v5/user/query-sub-members", kwargs={}, signed=True, query={}
    ),
    RouteCase(
        "get_member_wallet_types",
        "GET",
        "/v5/user/get-member-type",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase("get_smp_group", "GET", "/v5/account/smp-group", kwargs={}, query={}),
    RouteCase(
        "get_trade_behavior_config", "GET", "/v5/account/user-setting-config", kwargs={}, query={}
    ),
    RouteCase(
        "set_delta_mode",
        "POST",
        "/v5/account/set-delta-mode",
        kwargs={"delta_enable": "1"},
        body={"deltaEnable": "1"},
    ),
    RouteCase(
        "set_spot_hedging",
        "POST",
        "/v5/account/set-hedging-mode",
        kwargs={"mode": "ON"},
        body={"setHedgingMode": "ON"},
    ),
    RouteCase(
        "set_price_limit_behavior",
        "POST",
        "/v5/account/set-limit-px-action",
        kwargs={"category": "spot", "modify_enable": True},
        body={"category": "spot", "modifyEnable": True},
    ),
    RouteCase(
        "get_closed_option_positions",
        "GET",
        "/v5/position/get-closed-positions",
        kwargs={"category": "option", "limit": 100},
        query={"category": "option", "limit": "100"},
    ),
    RouteCase(
        "get_move_position_history",
        "GET",
        "/v5/position/move-history",
        kwargs={"category": "option", "limit": 200, "status": "Filled"},
        query={"category": "option", "status": "Filled", "limit": "200"},
    ),
    RouteCase(
        "move_positions",
        "POST",
        "/v5/position/move-positions",
        kwargs={
            "from_uid": "1",
            "to_uid": "2",
            "legs": [
                {
                    "category": "linear",
                    "symbol": "BTCUSDT",
                    "side": "Sell",
                    "qty": "0.01",
                    "price": "50000",
                }
            ],
        },
        body={
            "fromUid": "1",
            "toUid": "2",
            "list": [
                {
                    "category": "linear",
                    "symbol": "BTCUSDT",
                    "side": "Sell",
                    "qty": "0.01",
                    "price": "50000",
                }
            ],
        },
    ),
    RouteCase(
        "get_account_instruments",
        "GET",
        "/v5/account/instruments-info",
        kwargs={"category": "linear"},
        signed=True,
        query={"category": "linear"},
    ),
    RouteCase(
        "get_dcp_info", "GET", "/v5/account/query-dcp-info", kwargs={}, signed=True, query={}
    ),
    RouteCase("get_coin_greeks", "GET", "/v5/asset/coin-greeks", kwargs={}, signed=True, query={}),
    RouteCase(
        "repay_liability", "POST", "/v5/account/quick-repayment", kwargs={}, signed=True, body={}
    ),
    RouteCase(
        "set_collateral_coin",
        "POST",
        "/v5/account/set-collateral-switch",
        kwargs={"coin": "BTC", "collateral_switch": "ON"},
        signed=True,
        body={"coin": "BTC", "collateralSwitch": "ON"},
    ),
    RouteCase(
        "batch_set_collateral_coins",
        "POST",
        "/v5/account/set-collateral-switch-batch",
        kwargs={"request": [{"coin": "BTC", "collateralSwitch": "ON"}]},
        signed=True,
        body={"request": [{"coin": "BTC", "collateralSwitch": "ON"}]},
    ),
    RouteCase(
        "get_asset_overview", "GET", "/v5/asset/asset-overview", kwargs={}, signed=True, query={}
    ),
    RouteCase(
        "get_delivery_records",
        "GET",
        "/v5/asset/delivery-record",
        kwargs={
            "category": "linear",
            "start_time": 1700000000000,
            "end_time": 1700000060000,
            "limit": 10,
        },
        signed=True,
        query={
            "category": "linear",
            "startTime": "1700000000000",
            "endTime": "1700000060000",
            "limit": "10",
        },
    ),
    RouteCase(
        "get_settlement_records",
        "GET",
        "/v5/asset/settlement-record",
        kwargs={
            "category": "linear",
            "start_time": 1700000000000,
            "end_time": 1700000060000,
            "limit": 10,
        },
        signed=True,
        query={
            "category": "linear",
            "startTime": "1700000000000",
            "endTime": "1700000060000",
            "limit": "10",
        },
    ),
    RouteCase(
        "get_funding_account_history",
        "GET",
        "/v5/asset/fundinghistory",
        kwargs={"create_time_from": "1700000000", "create_time_to": "1700000600", "limit": "10"},
        signed=True,
        query={"createTimeFrom": "1700000000", "createTimeTo": "1700000600", "limit": "10"},
    ),
    RouteCase(
        "request_convert_quote",
        "POST",
        "/v5/asset/exchange/quote-apply",
        kwargs={
            "account_type": "eb_convert_funding",
            "from_coin": "ETH",
            "to_coin": "BTC",
            "request_coin": "ETH",
            "request_amount": "0.1",
        },
        signed=True,
        body={
            "accountType": "eb_convert_funding",
            "fromCoin": "ETH",
            "toCoin": "BTC",
            "requestCoin": "ETH",
            "requestAmount": "0.1",
        },
    ),
    RouteCase(
        "execute_convert_quote",
        "POST",
        "/v5/asset/exchange/convert-execute",
        kwargs={"quote_tx_id": "quote-1"},
        signed=True,
        body={"quoteTxId": "quote-1"},
    ),
    RouteCase(
        "get_convert_result",
        "GET",
        "/v5/asset/exchange/convert-result-query",
        kwargs={"quote_tx_id": "quote-1", "account_type": "eb_convert_funding"},
        signed=True,
        query={"quoteTxId": "quote-1", "accountType": "eb_convert_funding"},
    ),
    RouteCase(
        "get_full_orderbook",
        "GET",
        "/v5/market/full_orderbook",
        kwargs={"category": "linear", "product_symbol": "BTCUSDT"},
        signed=False,
        query={"category": "linear", "symbol": "BTCUSDT"},
    ),
    RouteCase(
        "get_rpi_orderbook",
        "GET",
        "/v5/market/rpi_orderbook",
        kwargs={"product_symbol": "BTCUSDT", "limit": 10},
        signed=False,
        query={"symbol": "BTCUSDT", "limit": "10"},
    ),
    RouteCase(
        "confirm_pending_mmr",
        "POST",
        "/v5/position/confirm-pending-mmr",
        kwargs={"category": "linear", "product_symbol": "BTCUSDT"},
        signed=True,
        body={"category": "linear", "symbol": "BTCUSDT"},
    ),
    RouteCase(
        "get_position_symbol_info",
        "GET",
        "/v5/position/symbol-info",
        kwargs={"category": "linear"},
        signed=True,
        query={"category": "linear"},
    ),
    RouteCase("get_system_status", "GET", "/v5/system/status", kwargs={}, signed=False, query={}),
    RouteCase("get_api_key_info", "GET", "/v5/user/query-api", kwargs={}, signed=True, query={}),
    RouteCase(
        "get_option_asset_info",
        "GET",
        "/v5/account/option-asset-info",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_portfolio_margin_info",
        "GET",
        "/v5/asset/portfolio-margin",
        kwargs={},
        signed=True,
        query={},
    ),
    RouteCase(
        "get_repayment_info", "GET", "/v5/account/pay-info", kwargs={}, signed=True, query={}
    ),
    RouteCase(
        "get_trade_analysis",
        "GET",
        "/v5/account/trade-info-for-analysis",
        kwargs={"product_symbol": "BTCUSDT"},
        signed=True,
        query={"symbol": "BTCUSDT"},
    ),
    RouteCase(
        "get_total_members_assets",
        "GET",
        "/v5/asset/total-members-assets",
        kwargs={},
        signed=True,
        query={},
    ),
    _get(
        "get_mark_price_kline",
        "/v5/market/mark-price-kline",
        LINEAR,
        "1m",
        signed=False,
        query={"symbol": "BTCUSDT", "category": "linear", "interval": "1"},
    ),
    _get(
        "get_index_price_kline",
        "/v5/market/index-price-kline",
        LINEAR,
        "1m",
        signed=False,
        query={"symbol": "BTCUSDT", "category": "linear", "interval": "1"},
    ),
    _get(
        "get_premium_index_price_kline",
        "/v5/market/premium-index-price-kline",
        LINEAR,
        "1m",
        signed=False,
        query={"symbol": "BTCUSDT", "category": "linear", "interval": "1"},
    ),
    _post(
        "set_spot_margin_leverage",
        "/v5/spot-margin-trade/set-leverage",
        "4",
        currency="USDT",
        body={"leverage": "4", "currency": "USDT"},
    ),
    _post(
        "set_spot_margin_mode",
        "/v5/spot-margin-trade/switch-mode",
        "1",
        body={"spotMarginMode": "1"},
    ),
    _post(
        "create_strategy",
        "/v5/strategy/create",
        "UTA_USDT",
        LINEAR,
        "Buy",
        "twap",
        size="1",
        duration=600,
        interval=30,
        reduce_only=False,
        body={
            "category": "UTA_USDT",
            "symbol": "BTCUSDT",
            "side": "Buy",
            "strategyType": "twap",
            "size": "1",
            "duration": 600,
            "interval": 30,
            "reduceOnly": False,
        },
    ),
    _post("stop_strategy", "/v5/strategy/stop", "s1", body={"strategyId": "s1"}),
    _get("get_strategy_list", "/v5/strategy/list", page_size=50, query={"pageSize": "50"}),
    _get("get_strategy_orders", "/v5/strategy/order-list", "s1", query={"strategyId": "s1"}),
    # Market data (public)
    _get(
        "get_instruments_info",
        "/v5/market/instruments-info",
        "linear",
        signed=False,
        query={"category": "linear"},
    ),
    _get(
        "get_kline",
        "/v5/market/kline",
        LINEAR,
        "1m",
        signed=False,
        query={"symbol": "BTCUSDT", "category": "linear", "interval": "1"},
    ),
    _get(
        "get_orderbook",
        "/v5/market/orderbook",
        LINEAR,
        signed=False,
        query={"symbol": "BTCUSDT", "category": "linear"},
    ),
    _get("get_tickers", "/v5/market/tickers", "spot", signed=False, query={"category": "spot"}),
    _get("get_funding_rate_history", "/v5/market/funding/history", LINEAR, signed=False),
    _get(
        "get_public_trade_history",
        "/v5/market/recent-trade",
        LINEAR,
        signed=False,
        query={"symbol": "BTCUSDT"},
    ),
    _get(
        "get_open_interest",
        "/v5/market/open-interest",
        LINEAR,
        "5min",
        signed=False,
        query={"intervalTime": "5min"},
    ),
    _get(
        "get_long_short_ratio",
        "/v5/market/account-ratio",
        LINEAR,
        "1h",
        signed=False,
        query={"period": "1h"},
    ),
    _get(
        "get_historical_volatility",
        "/v5/market/historical-volatility",
        "option",
        "BTC",
        signed=False,
        query={"category": "option", "baseCoin": "BTC"},
    ),
    _get("get_insurance_pool", "/v5/market/insurance", "USDT", signed=False),
    _get(
        "get_delivery_price",
        "/v5/market/delivery-price",
        "linear",
        signed=False,
        query={"category": "linear"},
    ),
    _get("get_order_price_limit", "/v5/market/price-limit", LINEAR, signed=False),
    _get("get_adl_alert", "/v5/market/adlAlert", LINEAR, signed=False),
    _get("get_risk_limit", "/v5/market/risk-limit", "linear", signed=False),
    _get("get_spread_instruments", "/v5/spread/instrument", signed=False),
    _get(
        "get_spread_orderbook",
        "/v5/spread/orderbook",
        "SOLUSDT_SOL/USDT",
        signed=False,
        query={"symbol": "SOLUSDT_SOL/USDT"},
    ),
    _get("get_spread_tickers", "/v5/spread/tickers", "SOLUSDT_SOL/USDT", signed=False),
    _get("get_spread_recent_trades", "/v5/spread/recent-trade", "SOLUSDT_SOL/USDT", signed=False),
    # Trade
    _post(
        "place_order",
        "/v5/order/create",
        LINEAR,
        "Buy",
        "Limit",
        "1",
        price="100",
        body={"symbol": "BTCUSDT", "category": "linear", "side": "Buy", "orderType": "Limit"},
    ),
    _post(
        "place_market_order",
        "/v5/order/create",
        LINEAR,
        "Sell",
        "1",
        body={"orderType": "Market"},
    ),
    _post("place_market_buy_order", "/v5/order/create", LINEAR, "1", body={"side": "Buy"}),
    _post("place_market_sell_order", "/v5/order/create", LINEAR, "1", body={"side": "Sell"}),
    _post(
        "place_limit_order",
        "/v5/order/create",
        LINEAR,
        "Buy",
        "1",
        "100",
        body={"orderType": "Limit", "price": "100"},
    ),
    _post("place_limit_buy_order", "/v5/order/create", LINEAR, "1", "100", body={"side": "Buy"}),
    _post("place_limit_sell_order", "/v5/order/create", LINEAR, "1", "100", body={"side": "Sell"}),
    _post(
        "place_post_only_limit_order",
        "/v5/order/create",
        LINEAR,
        "Buy",
        "1",
        "100",
        body={"timeInForce": "PostOnly"},
    ),
    _post(
        "place_post_only_limit_buy_order",
        "/v5/order/create",
        LINEAR,
        "1",
        "100",
        body={"side": "Buy", "timeInForce": "PostOnly"},
    ),
    _post(
        "place_post_only_limit_sell_order",
        "/v5/order/create",
        LINEAR,
        "1",
        "100",
        body={"side": "Sell", "timeInForce": "PostOnly"},
    ),
    _post(
        "pre_check_order",
        "/v5/order/pre-check",
        LINEAR,
        "Buy",
        "Limit",
        "1",
        price="100",
        body={"symbol": "BTCUSDT", "category": "linear"},
    ),
    _post(
        "amend_order",
        "/v5/order/amend",
        LINEAR,
        orderId="order-1",
        price="101",
        body={"orderId": "order-1", "symbol": "BTCUSDT"},
    ),
    _post(
        "cancel_order",
        "/v5/order/cancel",
        LINEAR,
        orderId="order-1",
        body={"orderId": "order-1", "symbol": "BTCUSDT"},
    ),
    _get("get_open_orders", "/v5/order/realtime", "linear", LINEAR, query={"symbol": "BTCUSDT"}),
    _post(
        "cancel_all_orders",
        "/v5/order/cancel-all",
        "linear",
        LINEAR,
        body={"category": "linear", "symbol": "BTCUSDT"},
    ),
    _get("get_order_history", "/v5/order/history", "linear", LINEAR),
    _get("get_execution_list", "/v5/execution/list", "linear", LINEAR),
    _post("place_batch_order", "/v5/order/create-batch", BATCH, "linear"),
    _post("amend_batch_order", "/v5/order/amend-batch", BATCH, "linear"),
    _post("cancel_batch_orders", "/v5/order/cancel-batch", BATCH, "linear"),
    _post(
        "set_disconnected_cancel_all",
        "/v5/order/disconnected-cancel-all",
        10,
        body={"timeWindow": 10},
    ),
    _get(
        "get_borrow_quota",
        "/v5/order/spot-borrow-check",
        SPOT,
        "Buy",
        query={"category": "spot", "symbol": "BTCUSDT", "side": "Buy"},
    ),
    # Spot margin (UTA)
    _get("get_vip_margin_data", "/v5/spot-margin-trade/data"),
    _get("get_collateral", "/v5/spot-margin-trade/collateral", "BTC"),
    _get("get_historical_interest_rate", "/v5/spot-margin-trade/interest-rate-history", "USDT"),
    _get("get_status_and_leverage", "/v5/spot-margin-trade/state"),
    _get("get_margin_max_borrowable", "/v5/spot-margin-trade/max-borrowable", "USDT"),
    _get("get_margin_position_tiers", "/v5/spot-margin-trade/position-tiers", "USDT"),
    _get("get_margin_coin_state", "/v5/spot-margin-trade/coinstate", "USDT"),
    _get(
        "get_margin_repayment_available_amount",
        "/v5/spot-margin-trade/repayment-available-amount",
        "USDT",
    ),
    _post("set_margin_auto_repay_mode", "/v5/spot-margin-trade/set-auto-repay-mode", "1", "USDT"),
    _get("get_margin_auto_repay_mode", "/v5/spot-margin-trade/get-auto-repay-mode", "USDT"),
    _get("get_fixed_borrow_quote", "/v5/spot-margin-trade/fixedborrow-order-quote", "USDT"),
    _post(
        "borrow_fixed_rate",
        "/v5/spot-margin-trade/fixedborrow",
        "USDT",
        "100",
        "0.05",
        "7",
    ),
    _post("renew_fixed_rate_borrow", "/v5/spot-margin-trade/fixedborrow-renew", "loan-1"),
    _get("get_fixed_borrow_orders", "/v5/spot-margin-trade/fixedborrow-order-info"),
    _get("get_fixed_borrow_contracts", "/v5/spot-margin-trade/fixedborrow-contract-info"),
    _get("get_margin_liability", "/v5/spot-margin-trade/liability", "USDT"),
    _get(
        "get_flexible_borrow_inventory",
        "/v5/spot-margin-trade/flexible-available-inventory",
        "USDT",
    ),
    _get(
        "get_fixed_borrow_inventory",
        "/v5/spot-margin-trade/fixed-available-inventory",
        "USDT",
        "7",
        "0.05",
    ),
    # Spread trading (private)
    _post(
        "place_spread_order",
        "/v5/spread/order/create",
        "SOLUSDT_SOL/USDT",
        "Buy",
        "Limit",
        "0.1",
        price="21",
    ),
    _post(
        "amend_spread_order",
        "/v5/spread/order/amend",
        "SOLUSDT_SOL/USDT",
        order_id="spread-1",
        price="22",
    ),
    _post("cancel_spread_order", "/v5/spread/order/cancel", order_id="spread-1"),
    _post("cancel_all_spread_orders", "/v5/spread/order/cancel-all", symbol="SOLUSDT_SOL/USDT"),
    _get("get_spread_open_orders", "/v5/spread/order/realtime"),
    _get("get_spread_order_history", "/v5/spread/order/history"),
    _get("get_spread_trade_history", "/v5/spread/execution/list"),
    _get("get_spread_max_qty", "/v5/spread/max-qty", "SOLUSDT_SOL/USDT", "1", "21"),
    # Position
    _get(
        "get_positions",
        "/v5/position/list",
        "linear",
        LINEAR,
        query={"category": "linear", "symbol": "BTCUSDT"},
    ),
    _post(
        "set_leverage",
        "/v5/position/set-leverage",
        LINEAR,
        "5",
        body={"symbol": "BTCUSDT", "buyLeverage": "5", "sellLeverage": "5"},
    ),
    _post(
        "switch_position_mode",
        "/v5/position/switch-mode",
        3,
        LINEAR,
        body={"symbol": "BTCUSDT", "mode": 3},
    ),
    _post(
        "set_trading_stop",
        "/v5/position/trading-stop",
        LINEAR,
        "Full",
        0,
        take_profit="120",
        body={"symbol": "BTCUSDT", "tpslMode": "Full", "takeProfit": "120"},
    ),
    _post(
        "add_position_margin",
        "/v5/position/add-margin",
        LINEAR,
        "10",
        body={"symbol": "BTCUSDT", "margin": "10"},
    ),
    _post(
        "set_auto_add_margin",
        "/v5/position/set-auto-add-margin",
        LINEAR,
        True,
        body={"symbol": "BTCUSDT", "autoAddMargin": 1},
    ),
    _get("get_closed_pnl", "/v5/position/closed-pnl", "linear", LINEAR),
    # Account
    _get(
        "get_wallet_balance",
        "/v5/account/wallet-balance",
        "USDT",
        query={"accountType": "UNIFIED", "coin": "USDT"},
    ),
    _get(
        "get_transferable_amount",
        "/v5/account/withdrawal",
        ["USDT", "BTC"],
        query={"coinName": "USDT,BTC"},
    ),
    _post("upgrade_to_unified_trading_account", "/v5/account/upgrade-to-uta"),
    _get("get_borrow_history", "/v5/account/borrow-history", "USDT"),
    _get("get_collateral_info", "/v5/account/collateral-info", "USDT"),
    _post("manual_borrow", "/v5/account/borrow", "USDT", "10", body={"coin": "USDT"}),
    _post("manual_repay", "/v5/account/repay", "USDT", "10"),
    _post("manual_repay_without_conversion", "/v5/account/no-convert-repay", "USDT", "10"),
    _get("get_spot_fee_rates", "/v5/account/fee-rate", SPOT, query={"category": "spot"}),
    _get("get_linear_fee_rates", "/v5/account/fee-rate", LINEAR, query={"category": "linear"}),
    _get(
        "get_inverse_fee_rates",
        "/v5/account/fee-rate",
        "BTC-USD-SWAP",
        query={"category": "inverse"},
    ),
    _get(
        "get_option_fee_rates",
        "/v5/account/fee-rate",
        None,
        "BTC",
        query={"category": "option", "baseCoin": "BTC"},
    ),
    _get("get_account_info", "/v5/account/info"),
    _get("get_transaction_log", "/v5/account/transaction-log", "UNIFIED"),
    _post(
        "set_margin_mode",
        "/v5/account/set-margin-mode",
        "REGULAR_MARGIN",
        body={"setMarginMode": "REGULAR_MARGIN"},
    ),
    # Asset
    _get("get_coin_info", "/v5/asset/coin/query-info", "USDT"),
    _get("get_sub_uid", "/v5/asset/transfer/query-sub-member-list"),
    _get("get_spot_asset_info", "/v5/asset/transfer/query-asset-info", "USDT"),
    _get(
        "get_coins_balance",
        "/v5/asset/transfer/query-account-coins-balance",
        "FUND",
        query={"accountType": "FUND"},
    ),
    _get(
        "get_coin_balance",
        "/v5/asset/transfer/query-account-coin-balance",
        "FUND",
        "USDT",
        query={"accountType": "FUND", "coin": "USDT"},
    ),
    _get("get_withdrawable_amount", "/v5/asset/withdraw/withdrawable-amount", "USDT"),
    _get("get_internal_transfer_records", "/v5/asset/transfer/query-inter-transfer-list"),
    _get(
        "get_transferable_coin",
        "/v5/asset/transfer/query-transfer-coin-list",
        "FUND",
        "UNIFIED",
    ),
    _post(
        "create_internal_transfer",
        "/v5/asset/transfer/inter-transfer",
        "USDT",
        "1",
        "FUND",
        "UNIFIED",
        transferId="42b3f4f1-6e4d-4f7e-9c5d-0c5e1f0a1b2c",
        body={"coin": "USDT", "fromAccountType": "FUND", "toAccountType": "UNIFIED"},
    ),
    _post(
        "create_universal_transfer",
        "/v5/asset/transfer/universal-transfer",
        "USDT",
        "1",
        1,
        2,
        "FUND",
        "UNIFIED",
        transferId="42b3f4f1-6e4d-4f7e-9c5d-0c5e1f0a1b2d",
    ),
    _get("get_universal_transfer_records", "/v5/asset/transfer/query-universal-transfer-list"),
    _post("set_deposit_account", "/v5/asset/deposit/deposit-to-account", "FUND"),
    _get("get_deposit_records", "/v5/asset/deposit/query-record"),
    _get("get_sub_deposit_records", "/v5/asset/deposit/query-sub-member-record", "123"),
    _get("get_internal_deposit_records", "/v5/asset/deposit/query-internal-record"),
    _get("get_master_deposit_address", "/v5/asset/deposit/query-address", "USDT"),
    # Earn (public product catalogues)
    _get("get_earn_products", "/v5/earn/product", "FlexibleSaving", signed=False),
    _get(
        "get_advanced_earn_products",
        "/v5/earn/advance/product",
        "DualAssets",
        signed=False,
    ),
    _get(
        "get_advanced_earn_product_quote",
        "/v5/earn/advance/product-extra-info",
        "DualAssets",
        "product-1",
        signed=False,
    ),
    _get("get_liquidity_mining_products", "/v5/earn/liquidity-mining/product", signed=False),
    _get("get_fixed_earn_products", "/v5/earn/fixed-term/product", signed=False),
    _get("get_hold_to_earn_products", "/v5/earn/hold-to-earn/product", signed=False),
    _get("get_byusdt_product", "/v5/earn/token/product", signed=False),
    _get("get_byusdt_apr_history", "/v5/earn/token/history-apr", 1, signed=False),
    _get("get_rwa_earn_products", "/v5/earn/rwa/product", "USDT", signed=False),
    _get("get_rwa_earn_nav_chart", "/v5/earn/rwa/nav-chart", "7", signed=False),
    _get(
        "get_earn_apr_history",
        "/v5/earn/apr-history",
        "OnChain",
        "product-1",
        signed=False,
    ),
    _get("get_launchpool_projects", "/v5/spot-x/launchpool/project/list", 1, signed=False),
    # Earn (private)
    _post(
        "place_earn_order",
        "/v5/earn/place-order",
        "FlexibleSaving",
        "Stake",
        "FUND",
        "1",
        "USDT",
        "430",
        "earn-1",
    ),
    _get("get_earn_order_history", "/v5/earn/order", "FlexibleSaving"),
    _get("get_earn_positions", "/v5/earn/position", "FlexibleSaving"),
    _get("get_earn_yield_history", "/v5/earn/yield", "FlexibleSaving"),
    _get("get_earn_hourly_yield_history", "/v5/earn/hourly-yield"),
    _get("get_earn_coupons", "/v5/earn/coupons", "FlexibleSaving"),
    _post(
        "set_earn_auto_reinvest",
        "/v5/earn/position/modify",
        430,
        5001,
        1,
        body={"category": "OnChain"},
    ),
    _post(
        "place_advanced_earn_order",
        "/v5/earn/advance/place-order",
        "DualAssets",
        "product-2",
        "Stake",
        "FUND",
        "adv-1",
        amount="10",
        coin="USDT",
        dualAssetsExtra={"orderDirection": "Buy", "selectPrice": "1", "apyE8": "1"},
    ),
    _get("get_advanced_earn_positions", "/v5/earn/advance/position", "DualAssets"),
    _get("get_advanced_earn_orders", "/v5/earn/advance/order", "DualAssets"),
    _get(
        "get_advanced_earn_redeem_estimates",
        "/v5/earn/advance/get-redeem-est-amount-list",
        "SmartLeverage",
        "pos-1",
    ),
    _get(
        "get_double_win_leverage",
        "/v5/earn/advance/double-win-leverage",
        "product-3",
        "100",
        "90",
        "110",
    ),
    _get("get_liquidity_mining_positions", "/v5/earn/liquidity-mining/position"),
    _get("get_liquidity_mining_orders", "/v5/earn/liquidity-mining/order"),
    _get("get_liquidity_mining_yield_records", "/v5/earn/liquidity-mining/yield-records"),
    _get(
        "get_liquidity_mining_liquidation_records",
        "/v5/earn/liquidity-mining/liquidation-records",
    ),
    _post(
        "add_liquidity_mining",
        "/v5/earn/liquidity-mining/add-liquidity",
        "36",
        "lm-1",
        quoteAmount="200",
        quoteAccountType="FUND",
        leverage="2",
    ),
    _post(
        "remove_liquidity_mining",
        "/v5/earn/liquidity-mining/remove-liquidity",
        "36",
        "lm-2",
        "5001",
        removeRate=50,
    ),
    _post(
        "reinvest_liquidity_mining",
        "/v5/earn/liquidity-mining/reinvest",
        "36",
        "lm-3",
        "5001",
    ),
    _post(
        "add_liquidity_mining_margin",
        "/v5/earn/liquidity-mining/add-margin",
        "36",
        "lm-4",
        "5001",
        "10",
        "FUND",
    ),
    _post("claim_liquidity_mining_interest", "/v5/earn/liquidity-mining/claim-interest", "36"),
    _get("get_fixed_earn_positions", "/v5/earn/fixed-term/position"),
    _get("get_fixed_earn_orders", "/v5/earn/fixed-term/order"),
    _post(
        "place_fixed_earn_order",
        "/v5/earn/fixed-term/place-order",
        "fixed-1",
        "FixedTermSaving",
        "USDT",
        "10",
        "FUND",
        "fixed-link-1",
    ),
    _post(
        "redeem_fixed_earn",
        "/v5/earn/fixed-term/redeem",
        "fixed-1",
        "FundPool",
        "pos-1",
    ),
    _post(
        "set_fixed_earn_auto_invest",
        "/v5/earn/fixed-term/position/auto-invest",
        "fixed-1",
        "FixedTermSaving",
        "pos-1",
        "Enable",
    ),
    _get("get_hold_to_earn_yield_history", "/v5/earn/hold-to-earn/yield-history", 20),
    _get("get_byusdt_orders", "/v5/earn/token/order"),
    _get("get_byusdt_position", "/v5/earn/token/position"),
    _get("get_byusdt_daily_yield", "/v5/earn/token/yield"),
    _get("get_byusdt_hourly_yield", "/v5/earn/token/hourly-yield"),
    _post(
        "place_byusdt_order",
        "/v5/earn/token/place-order",
        "Mint",
        "10",
        "FlexibleSaving",
        "by-1",
    ),
    _get("get_rwa_earn_positions", "/v5/earn/rwa/position"),
    _get("get_rwa_earn_orders", "/v5/earn/rwa/order"),
    _post(
        "place_rwa_earn_order",
        "/v5/earn/rwa/place-order",
        "7",
        "Stake",
        "USDT",
        "rwa-link-1",
        stakeAmount="10",
        accountType="FUND",
    ),
    # Spot-X Launchpool (private)
    _get("get_launchpool_current_staking", "/v5/spot-x/launchpool/user/current-staking"),
    _post("get_launchpool_activity_log", "/v5/spot-x/launchpool/user/activity-log"),
    _post("get_launchpool_history", "/v5/spot-x/launchpool/user/history"),
    # RFQ
    _get("get_rfq_public_trades", "/v5/rfq/public-trades", limit=20),
    _get("get_rfq_config", "/v5/rfq/config"),
    _post("create_rfq", "/v5/rfq/create-rfq", ["desk"], RFQ_LEGS),
    _post("cancel_rfq", "/v5/rfq/cancel-rfq", rfqId="rfq-1", body={"rfqId": "rfq-1"}),
    _post("cancel_all_rfqs", "/v5/rfq/cancel-all-rfq"),
    _post("accept_other_rfq_quote", "/v5/rfq/accept-other-quote", "rfq-1"),
    _post(
        "create_rfq_quote",
        "/v5/rfq/create-quote",
        "rfq-1",
        quoteBuyList=[{"category": "option", "symbol": "BTC-C", "price": "1"}],
    ),
    _post("execute_rfq_quote", "/v5/rfq/execute-quote", "rfq-1", "quote-1", "Buy"),
    _post("cancel_rfq_quote", "/v5/rfq/cancel-quote", quoteId="quote-1"),
    _post("cancel_all_rfq_quotes", "/v5/rfq/cancel-all-quotes"),
    _get("get_realtime_rfqs", "/v5/rfq/rfq-realtime"),
    _get("get_rfqs", "/v5/rfq/rfq-list"),
    _get("get_rfq_details", "/v5/rfq/rfq-detail-list"),
    _get("get_realtime_rfq_quotes", "/v5/rfq/quote-realtime"),
    _get("get_rfq_quotes", "/v5/rfq/quote-list"),
    _get("get_rfq_trade_history", "/v5/rfq/trade-list"),
)


@contextmanager
def _route_server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    body = json.dumps({"retCode": 0, "retMsg": "OK", "result": {}}).encode()

    class Handler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            received.put(
                {
                    "verb": self.command,
                    "path": self.path,
                    "sign": self.headers.get("X-BAPI-SIGN"),
                    "api_key": self.headers.get("X-BAPI-API-KEY"),
                    "body": self.rfile.read(length).decode() if length else "",
                }
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            self._handle()

        def do_POST(self) -> None:  # noqa: N802
            self._handle()

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)


def _native_client(base_url: str) -> Any:  # noqa: ANN401
    return native.BybitHttpClient(
        api_key="api-key",
        api_secret="api-secret",
        recv_window=5000,
        sync_server_time=False,
        timeout=10,
        base_url=base_url,
    )


def _fail_if_native_is_stale(exc: ValueError) -> None:
    # The installed extension can lag the Rust source until it is rebuilt with maturin.
    if str(exc).startswith(("unsupported Bybit public method", "unsupported Bybit private method")):
        pytest.fail(f"installed dcex._native predates this route: {exc}")
    raise exc


def _assert_route(case: RouteCase, received: queue.Queue[dict[str, Any]]) -> None:
    assert received.qsize() == 1, f"{case.method_name} sent {received.qsize()} requests"
    request = received.get_nowait()
    from tests.unit.wire_contracts import assert_wire_contract
    assert_wire_contract("bybit", case.method_name, request)
    split = urlsplit(request["path"])
    assert (request["verb"], split.path) == (case.verb, case.path)
    if case.signed:
        assert request["api_key"] == "api-key"
        assert request["sign"]
    else:
        assert request["sign"] is None
    query = dict(parse_qsl(split.query, keep_blank_values=True))
    for key, value in case.query.items():
        assert query.get(key) == value, (key, query)
    if case.verb == "POST":
        payload = json.loads(request["body"] or "{}")
        for key, value in case.body.items():
            assert payload.get(key) == value, (key, payload)
    else:
        assert request["body"] == ""


def _sync_client(base_url: str) -> Any:  # noqa: ANN401
    from dcex.bybit.client import Client

    client = Client(
        api_key="api-key",
        api_secret="api-secret",
        preload_product_table=False,
        sync_server_time=False,
    )
    client._native_client = _native_client(base_url)
    return client


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.method_name)
def test_sync_bybit_wrapper_hits_official_route(case: RouteCase) -> None:
    with _route_server() as (base_url, received):
        client = _sync_client(base_url)
        try:
            getattr(client, case.method_name)(*case.args, **case.kwargs)
        except ValueError as exc:
            _fail_if_native_is_stale(exc)
        finally:
            client.close()
        _assert_route(case, received)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.method_name)
def test_async_bybit_wrapper_hits_official_route(case: RouteCase) -> None:
    from dcex.async_support.bybit.client import Client

    async def run(base_url: str) -> None:
        client = Client(
            api_key="api-key",
            api_secret="api-secret",
            preload_product_table=False,
            sync_server_time=False,
        )
        client._native_client = _native_client(base_url)
        await client.async_init()
        try:
            await getattr(client, case.method_name)(*case.args, **case.kwargs)
        finally:
            await client.close()

    with _route_server() as (base_url, received):
        try:
            asyncio.run(run(base_url))
        except ValueError as exc:
            _fail_if_native_is_stale(exc)
        _assert_route(case, received)


def _public_wrapper_names(module: str) -> set[str]:
    from importlib import import_module

    client_cls = import_module(module).Client
    return {
        name
        for name, value in vars(client_cls).items()
        if callable(value) and not name.startswith("_")
    } | {
        name
        for base in client_cls.__mro__[1:]
        if base.__module__.startswith(module.rsplit(".", 1)[0] + "._")
        and base.__module__.endswith("_http")
        and not base.__module__.endswith("_http_manager")
        for name, value in vars(base).items()
        if callable(value) and not name.startswith("_")
    }


@pytest.mark.parametrize("module", ["dcex.bybit.client", "dcex.async_support.bybit.client"])
def test_every_bybit_endpoint_wrapper_has_a_route_case(module: str) -> None:
    names = _public_wrapper_names(module) - {"close", "async_init"}
    from tests.unit.test_bybit_schema_requests import CASES as COMPLETION_CASES

    covered = {case.method_name for case in CASES} | {case["name"] for case in COMPLETION_CASES}
    assert sorted(names - covered) == []
    assert sorted(covered - names) == []
