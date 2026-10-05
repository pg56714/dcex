"""
Offline route coverage for every MEXC REST wrapper.

Each public wrapper (sync and async) is driven through the real Rust native
client against a local HTTP server, asserting the HTTP method and the official
MEXC REST path documented at https://www.mexc.com/api-docs/spot-v3/ and
https://www.mexc.com/api-docs/futures/.
"""

# ruff: noqa: ANN401, D103

from __future__ import annotations

import ast
import hashlib
import hmac
import json
import queue
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
SYMBOL = "BTC-USDT-SPOT"
SWAP = "BTC_USDT"

# method name -> (kwargs, HTTP method, official path, signed?)
CASES: dict[str, tuple[dict[str, Any], str, str, bool]] = {
    "close_spot_listen_key": ({"listen_key": "test-key"}, "DELETE", "/api/v3/userDataStream", True),
    "keep_alive_spot_listen_key": (
        {"listen_key": "test-key"},
        "PUT",
        "/api/v3/userDataStream",
        True,
    ),
    "get_spot_listen_keys": ({}, "GET", "/api/v3/userDataStream", True),
    "create_spot_listen_key": ({}, "POST", "/api/v3/userDataStream", True),
    "create_deposit_address": (
        {"coin": "USDT", "network": "TRC20"},
        "POST",
        "/api/v3/capital/deposit/address",
        True,
    ),
    "delete_sub_account_api_key": (
        {"sub_account": "sub1", "api_key": "test-key", "recv_window": 5000},
        "DELETE",
        "/api/v3/sub-account/apiKey",
        True,
    ),
    "create_sub_account_api_key": (
        {
            "sub_account": "sub1",
            "note": "trading",
            "permissions": "SPOT_ACCOUNT_READ",
            "ip": "127.0.0.1",
            "recv_window": 5000,
        },
        "POST",
        "/api/v3/sub-account/apiKey",
        True,
    ),
    "get_sub_account_api_keys": (
        {"sub_account": "sub1", "recv_window": 5000},
        "GET",
        "/api/v3/sub-account/apiKey",
        True,
    ),
    "get_stp_strategy_group": (
        {"trade_group_name": "group1"},
        "GET",
        "/api/v3/strategy/group",
        True,
    ),
    "remove_stp_strategy_group_members": (
        {"uid": "1001,1002", "trade_group_id": "91"},
        "DELETE",
        "/api/v3/strategy/group/uid",
        True,
    ),
    "get_withdrawal_addresses": (
        {"coin": "USDT", "page": 1, "limit": 1},
        "GET",
        "/api/v3/capital/withdraw/address",
        True,
    ),
    "delete_stp_strategy_group": (
        {"trade_group_id": "91"},
        "DELETE",
        "/api/v3/strategy/group",
        True,
    ),
    "create_stp_strategy_group": (
        {"trade_group_name": "group1"},
        "POST",
        "/api/v3/strategy/group",
        True,
    ),
    "add_stp_strategy_group_members": (
        {"uid": "1001,1002", "trade_group_id": "91"},
        "POST",
        "/api/v3/strategy/group/uid",
        True,
    ),
    "get_spot_offline_symbols": ({}, "GET", "/api/v3/symbol/offline", False),
    "get_announcements": (
        {"language": "en-US", "page": 1, "limit": 20},
        "GET",
        "/api/v3/announcements",
        False,
    ),
    "get_contract_supported_currencies": ({}, "GET", "/api/v1/contract/support_currencies", False),
    "get_uid": ({}, "GET", "/api/v3/uid", True),
    "get_api_key_info": ({"access_key": "query-key"}, "GET", "/api/v3/apiKeyInfo", True),
    "set_api_key_ip_whitelist": (
        {"api_key": "query-key", "ip_whitelist": "127.0.0.1,192.0.2.1", "note": "trading"},
        "POST",
        "/api/v3/apiKeyInfo",
        True,
    ),
    "get_convertible_assets": ({}, "GET", "/api/v3/capital/convert/list", True),
    "convert_dust": ({"assets": "BTC,ETH"}, "POST", "/api/v3/capital/convert", True),
    "get_dust_conversion_history": (
        {"start_time": 1700000000000, "end_time": 1700000010000, "page": 1, "limit": 100},
        "GET",
        "/api/v3/capital/convert",
        True,
    ),
    "create_sub_account": (
        {"sub_account": "sub1", "note": "trading", "recv_window": 5000},
        "POST",
        "/api/v3/sub-account/virtualSubAccount",
        True,
    ),
    "get_contract_profit_rate": (
        {"period_type": 1},
        "GET",
        "/api/v1/private/account/profit_rate/1",
        True,
    ),
    "get_contract_fee_deduction_config": (
        {},
        "GET",
        "/api/v1/private/account/feeDeductConfigs",
        True,
    ),
    "get_contract_fee_discount_config": (
        {},
        "GET",
        "/api/v1/private/account/config/contractFeeDiscountConfig",
        True,
    ),
    "get_contract_discount_usage": ({}, "GET", "/api/v1/private/account/discountType", True),
    "cancel_contract_batch_orders_by_external_id": (
        {
            "orders": [
                {"product_symbol": "BTC_USDT", "externalOid": "1"},
                {"product_symbol": "ETH_USDT", "externalOid": "2"},
            ]
        },
        "POST",
        "/api/v1/private/order/batch_cancel_with_external",
        True,
    ),
    "get_contract_batch_orders_by_external_id": (
        {
            "orders": [
                {"product_symbol": "BTC_USDT", "externalOid": "1"},
                {"product_symbol": "ETH_USDT", "externalOid": "2"},
            ]
        },
        "POST",
        "/api/v1/private/order/batch_query_with_external",
        True,
    ),
    "get_contract_closed_orders": (
        {"product_symbol": "BTC_USDT", "page_size": 10},
        "GET",
        "/api/v1/private/order/list/close_orders",
        True,
    ),
    "get_contract_fee_details": (
        {"product_symbol": "BTC_USDT", "page_size": 10, "ids": [11, 12]},
        "GET",
        "/api/v1/private/order/fee_details",
        True,
    ),
    "get_contract_30_day_fee_statistics": (
        {},
        "GET",
        "/api/v1/private/account/asset_book/order_deal_fee/total",
        True,
    ),
    "cancel_spot_all_orders": ({"all_symbols": True}, "DELETE", "/api/v3/order/all", True),
    "get_contract_open_stop_orders": (
        {"product_symbol": "BTC_USDT"},
        "GET",
        "/api/v1/private/stoporder/open_orders",
        True,
    ),
    # Spot market data
    "ping": ({}, "GET", "/api/v3/ping", False),
    "get_spot_time": ({}, "GET", "/api/v3/time", False),
    "get_spot_default_symbols": ({}, "GET", "/api/v3/defaultSymbols", False),
    "get_spot_exchange_info": ({}, "GET", "/api/v3/exchangeInfo", False),
    "get_spot_orderbook": ({"product_symbol": SYMBOL}, "GET", "/api/v3/depth", False),
    "get_spot_recent_trades": ({"product_symbol": SYMBOL}, "GET", "/api/v3/trades", False),
    "get_spot_agg_trades": ({"product_symbol": SYMBOL}, "GET", "/api/v3/aggTrades", False),
    "get_spot_klines": ({"product_symbol": SYMBOL}, "GET", "/api/v3/klines", False),
    "get_spot_avg_price": ({"product_symbol": SYMBOL}, "GET", "/api/v3/avgPrice", False),
    "get_spot_ticker_24hr": ({}, "GET", "/api/v3/ticker/24hr", False),
    "get_spot_ticker_price": ({}, "GET", "/api/v3/ticker/price", False),
    "get_spot_book_ticker": ({}, "GET", "/api/v3/ticker/bookTicker", False),
    # Spot account / wallet / sub-account
    "get_kyc_status": ({}, "GET", "/api/v3/kyc/status", True),
    "get_spot_self_symbols": ({}, "GET", "/api/v3/selfSymbols", True),
    "get_spot_account": ({}, "GET", "/api/v3/account", True),
    "get_spot_mx_deduct_status": ({}, "GET", "/api/v3/mxDeduct/enable", True),
    "set_spot_mx_deduct": ({"mxDeductEnable": True}, "POST", "/api/v3/mxDeduct/enable", True),
    "get_spot_symbol_commission": (
        {"product_symbol": SYMBOL},
        "GET",
        "/api/v3/tradeFee",
        True,
    ),
    "get_currency_info": ({}, "GET", "/api/v3/capital/config/getall", True),
    "get_deposit_history": ({}, "GET", "/api/v3/capital/deposit/hisrec", True),
    "get_withdraw_history": ({}, "GET", "/api/v3/capital/withdraw/history", True),
    "get_deposit_address": ({"coin": "USDT"}, "GET", "/api/v3/capital/deposit/address", True),
    "user_universal_transfer": (
        {"fromAccountType": "SPOT", "toAccountType": "FUTURES", "asset": "USDT", "amount": "1"},
        "POST",
        "/api/v3/capital/transfer",
        True,
    ),
    "get_user_universal_transfer_history": (
        {"fromAccountType": "SPOT", "toAccountType": "FUTURES"},
        "GET",
        "/api/v3/capital/transfer",
        True,
    ),
    "get_user_universal_transfer_by_id": (
        {"tranId": "123"},
        "GET",
        "/api/v3/capital/transfer/tranId",
        True,
    ),
    "get_internal_transfer_history": ({}, "GET", "/api/v3/capital/transfer/internal", True),
    "get_subaccounts": ({}, "GET", "/api/v3/sub-account/list", True),
    "get_subaccount_asset": ({"subAccount": "alpha"}, "GET", "/api/v3/sub-account/asset", True),
    "transfer_subaccount_assets": (
        {"fromAccountType": "SPOT", "toAccountType": "SPOT", "asset": "USDT", "amount": "1"},
        "POST",
        "/api/v3/capital/sub-account/universalTransfer",
        True,
    ),
    "get_subaccount_transfer_history": (
        {"fromAccountType": "SPOT", "toAccountType": "SPOT"},
        "GET",
        "/api/v3/capital/sub-account/universalTransfer",
        True,
    ),
    # Spot trading
    "test_spot_order": (
        {"product_symbol": SYMBOL, "side": "BUY", "type_": "LIMIT", "quantity": "1", "price": "1"},
        "POST",
        "/api/v3/order/test",
        True,
    ),
    "place_spot_order": (
        {"product_symbol": SYMBOL, "side": "BUY", "type_": "LIMIT", "quantity": "1", "price": "1"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_limit_order": (
        {"product_symbol": SYMBOL, "side": "BUY", "quantity": "1", "price": "1"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_limit_buy_order": (
        {"product_symbol": SYMBOL, "quantity": "1", "price": "1"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_limit_sell_order": (
        {"product_symbol": SYMBOL, "quantity": "1", "price": "1"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_post_only_limit_order": (
        {"product_symbol": SYMBOL, "side": "SELL", "quantity": "1", "price": "1"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_post_only_limit_buy_order": (
        {"product_symbol": SYMBOL, "quantity": "1", "price": "1"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_post_only_limit_sell_order": (
        {"product_symbol": SYMBOL, "quantity": "1", "price": "1"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_market_order": (
        {"product_symbol": SYMBOL, "side": "BUY", "quoteOrderQty": "10"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_market_buy_order": (
        {"product_symbol": SYMBOL, "quoteOrderQty": "10"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_market_sell_order": (
        {"product_symbol": SYMBOL, "quantity": "1"},
        "POST",
        "/api/v3/order",
        True,
    ),
    "place_spot_batch_orders": (
        {
            "batchOrders": [
                {
                    "symbol": "BTCUSDT",
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": "1",
                    "price": "1",
                }
            ]
        },
        "POST",
        "/api/v3/batchOrders",
        True,
    ),
    "cancel_spot_order": (
        {"product_symbol": SYMBOL, "orderId": "123"},
        "DELETE",
        "/api/v3/order",
        True,
    ),
    "cancel_spot_open_orders": ({"product_symbol": SYMBOL}, "DELETE", "/api/v3/openOrders", True),
    "get_spot_order": ({"product_symbol": SYMBOL, "orderId": "123"}, "GET", "/api/v3/order", True),
    "get_spot_open_orders": ({"product_symbol": SYMBOL}, "GET", "/api/v3/openOrders", True),
    "get_spot_all_orders": ({"product_symbol": SYMBOL}, "GET", "/api/v3/allOrders", True),
    "get_spot_my_trades": ({"product_symbol": SYMBOL}, "GET", "/api/v3/myTrades", True),
    # Contract market data
    "get_contract_time": ({}, "GET", "/api/v1/contract/ping", False),
    # Docs list only /detail/country; legacy /detail still answers with the same schema.
    "get_contract_details": ({}, "GET", "/api/v1/contract/detail/country", False),
    "get_contract_ticker": ({}, "GET", "/api/v1/contract/ticker", False),
    "get_contract_depth": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/depth/BTC_USDT",
        False,
    ),
    "get_contract_depth_commits": (
        {"product_symbol": SWAP, "limit": 20},
        "GET",
        "/api/v1/contract/depth_commits/BTC_USDT/20",
        False,
    ),
    "get_contract_index_price": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/index_price/BTC_USDT",
        False,
    ),
    "get_contract_fair_price": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/fair_price/BTC_USDT",
        False,
    ),
    "get_contract_funding_rate": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/funding_rate/BTC_USDT",
        False,
    ),
    "get_contract_kline": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/kline/BTC_USDT",
        False,
    ),
    "get_contract_index_price_kline": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/kline/index_price/BTC_USDT",
        False,
    ),
    "get_contract_fair_price_kline": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/kline/fair_price/BTC_USDT",
        False,
    ),
    "get_contract_deals": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/deals/BTC_USDT",
        False,
    ),
    "get_contract_risk_reverse": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/risk_reverse/BTC_USDT",
        False,
    ),
    "get_contract_risk_reverse_history": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/risk_reverse/history",
        False,
    ),
    "get_contract_funding_rate_history": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/contract/funding_rate/history",
        False,
    ),
    # Contract account / positions
    "get_contract_assets": ({}, "GET", "/api/v1/private/account/assets", True),
    "get_contract_asset": ({"currency": "USDT"}, "GET", "/api/v1/private/account/asset/USDT", True),
    "get_contract_transfer_records": ({}, "GET", "/api/v1/private/account/transfer_record", True),
    "get_contract_history_positions": (
        {},
        "GET",
        "/api/v1/private/position/list/history_positions",
        True,
    ),
    "get_contract_open_positions": ({}, "GET", "/api/v1/private/position/open_positions", True),
    "get_contract_funding_records": ({}, "GET", "/api/v1/private/position/funding_records", True),
    "get_contract_risk_limits": ({}, "GET", "/api/v1/private/account/risk_limit", True),
    "get_contract_trading_fee_rate": (
        {},
        "GET",
        "/api/v1/private/account/tiered_fee_rate/v2",
        True,
    ),
    "get_contract_leverage": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/private/position/leverage",
        True,
    ),
    "change_contract_margin": (
        {"positionId": 7, "amount": "1", "type_": "ADD"},
        "POST",
        "/api/v1/private/position/change_margin",
        True,
    ),
    "change_contract_auto_add_margin": (
        {"positionId": 7, "enabled": True},
        "POST",
        "/api/v1/private/position/change_auto_add_im",
        True,
    ),
    "change_contract_leverage": (
        {"leverage": 5, "positionId": 7},
        "POST",
        "/api/v1/private/position/change_leverage",
        True,
    ),
    "get_contract_position_mode": ({}, "GET", "/api/v1/private/position/position_mode", True),
    "change_contract_position_mode": (
        {"positionMode": 1},
        "POST",
        "/api/v1/private/position/change_position_mode",
        True,
    ),
    "change_contract_multi_asset_mode": (
        {"enabled": True},
        "POST",
        "/api/v1/private/multiAssets/changeMultiAssetMode/true",
        True,
    ),
    # Contract orders
    "place_contract_order": (
        {
            "product_symbol": SWAP,
            "side": 1,
            "type_": 1,
            "openType": 1,
            "vol": 1,
            "price": "1",
            "leverage": 5,
        },
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_limit_order": (
        {"product_symbol": SWAP, "side": 1, "price": "1", "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_limit_buy_order": (
        {"product_symbol": SWAP, "price": "1", "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_limit_sell_order": (
        {"product_symbol": SWAP, "price": "1", "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_post_only_order": (
        {"product_symbol": SWAP, "side": 3, "price": "1", "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_post_only_buy_order": (
        {"product_symbol": SWAP, "price": "1", "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_post_only_sell_order": (
        {"product_symbol": SWAP, "price": "1", "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_market_order": (
        {"product_symbol": SWAP, "side": 1, "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_market_buy_order": (
        {"product_symbol": SWAP, "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "place_contract_market_sell_order": (
        {"product_symbol": SWAP, "vol": 1, "leverage": 5},
        "POST",
        "/api/v1/private/order/create",
        True,
    ),
    "cancel_contract_orders": (
        {"orders": ["1", "2"]},
        "POST",
        "/api/v1/private/order/cancel",
        True,
    ),
    "cancel_contract_order": ({"order_id": "1"}, "POST", "/api/v1/private/order/cancel", True),
    "cancel_contract_order_with_external_id": (
        {"product_symbol": SWAP, "externalOid": "ext-1"},
        "POST",
        "/api/v1/private/order/cancel_with_external",
        True,
    ),
    "cancel_all_contract_orders": ({}, "POST", "/api/v1/private/order/cancel_all", True),
    "amend_contract_limit_order": (
        {"orderId": "1", "price": "2", "vol": "1"},
        "POST",
        "/api/v1/private/order/change_limit_order",
        True,
    ),
    "chase_contract_limit_order": (
        {"orderId": "1"},
        "POST",
        "/api/v1/private/order/chase_limit_order",
        True,
    ),
    "get_contract_open_order_count": (
        {},
        "GET",
        "/api/v1/private/order/open_order_total_count",
        True,
    ),
    "reverse_contract_position": (
        {"product_symbol": SWAP, "positionId": 7, "vol": "1"},
        "POST",
        "/api/v1/private/position/reverse",
        True,
    ),
    "close_all_contract_positions": ({}, "POST", "/api/v1/private/position/close_all", True),
    "get_contract_open_orders": ({}, "GET", "/api/v1/private/order/list/open_orders", True),
    "get_contract_history_orders": (
        {},
        "GET",
        "/api/v1/private/order/list/history_orders",
        True,
    ),
    "get_contract_order_by_external_id": (
        {"product_symbol": SWAP, "external_oid": "ext-1"},
        "GET",
        "/api/v1/private/order/external/BTC_USDT/ext-1",
        True,
    ),
    "get_contract_order": ({"order_id": "123"}, "GET", "/api/v1/private/order/get/123", True),
    "get_contract_orders": (
        {"order_ids": ["1", "2"]},
        "GET",
        "/api/v1/private/order/batch_query",
        True,
    ),
    "get_contract_order_deal_details": (
        {"order_id": "123"},
        "GET",
        "/api/v1/private/order/deal_details/123",
        True,
    ),
    "get_contract_order_deals": (
        {"product_symbol": SWAP},
        "GET",
        "/api/v1/private/order/list/order_deals/v3",
        True,
    ),
    # Plan / TP-SL / trailing orders
    "get_contract_plan_orders": ({}, "GET", "/api/v1/private/planorder/list/orders", True),
    "place_contract_plan_order": (
        {
            "product_symbol": SWAP,
            "vol": "1",
            "leverage": "5",
            "side": "1",
            "openType": "1",
            "triggerPrice": "100",
            "triggerType": "1",
            "executeCycle": "1",
            "orderType": "5",
            "trend": "1",
        },
        "POST",
        "/api/v1/private/planorder/place/v2",
        True,
    ),
    "amend_contract_plan_order": (
        {
            "product_symbol": SWAP,
            "orderId": "1",
            "triggerPrice": "100",
            "price": "99",
            "orderType": 1,
            "triggerType": 1,
            "trend": 1,
            "from_": 1,
        },
        "POST",
        "/api/v1/private/planorder/change_price",
        True,
    ),
    "cancel_contract_plan_orders": (
        {"orders": [{"symbol": "BTC_USDT", "orderId": "1"}]},
        "POST",
        "/api/v1/private/planorder/cancel",
        True,
    ),
    "cancel_all_contract_plan_orders": ({}, "POST", "/api/v1/private/planorder/cancel_all", True),
    "get_contract_stop_orders": ({}, "GET", "/api/v1/private/stoporder/list/orders", True),
    "place_contract_position_tpsl": (
        {
            "lossTrend": 1,
            "profitTrend": 1,
            "positionId": 7,
            "vol": "1",
            "stopLossPrice": "90",
            "takeProfitPrice": "110",
        },
        "POST",
        "/api/v1/private/stoporder/place",
        True,
    ),
    "cancel_contract_tpsl_orders": (
        {"orders": [{"stopPlanOrderId": "1"}]},
        "POST",
        "/api/v1/private/stoporder/cancel",
        True,
    ),
    "cancel_all_contract_tpsl_orders": ({}, "POST", "/api/v1/private/stoporder/cancel_all", True),
    "amend_contract_limit_tpsl": (
        {"orderId": "1", "stopLossPrice": "90"},
        "POST",
        "/api/v1/private/stoporder/change_price",
        True,
    ),
    "amend_contract_tpsl_order": (
        {"stopPlanOrderId": "1", "stopLossPrice": "90"},
        "POST",
        "/api/v1/private/stoporder/change_plan_price",
        True,
    ),
    "amend_contract_plan_tpsl": (
        {"product_symbol": SWAP, "orderId": "1", "stopLossPrice": "90"},
        "POST",
        "/api/v1/private/planorder/change_stop_order",
        True,
    ),
    "place_contract_trailing_order": (
        {
            "product_symbol": SWAP,
            "leverage": 5,
            "side": 1,
            "vol": "1",
            "openType": 1,
            "trend": 1,
            "backType": 1,
            "backValue": "0.01",
            "positionMode": 1,
        },
        "POST",
        "/api/v1/private/trackorder/place",
        True,
    ),
    "cancel_contract_trailing_order": (
        {"trackOrderId": "1"},
        "POST",
        "/api/v1/private/trackorder/cancel",
        True,
    ),
    "amend_contract_trailing_order": (
        {
            "product_symbol": SWAP,
            "trackOrderId": "1",
            "trend": 1,
            "backType": 1,
            "backValue": "0.02",
            "vol": "1",
        },
        "POST",
        "/api/v1/private/trackorder/change_order",
        True,
    ),
    "get_contract_trailing_orders": (
        {"states": [0]},
        "GET",
        "/api/v1/private/trackorder/list/orders",
        True,
    ),
}


COMPLETION_CASES = json.loads(
    (ROOT / "tests/fixtures/mexc_request_cases.json").read_text(encoding="utf-8")
)
CASES.update(
    {
        case["name"]: (case["kwargs"], case["method"], case["path"], True)
        for case in COMPLETION_CASES
    }
)
COMPLETION_BY_NAME = {case["name"]: case for case in COMPLETION_CASES}


def _wrapper_names(mode: str) -> set[str]:
    base = ROOT / "dcex"
    if mode == "async":
        base /= "async_support"
    names: set[str] = set()
    for path in sorted((base / "mexc").glob("_*_http.py")):
        if path.name == "_http_manager.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            for node in cls.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not (
                    node.name.startswith("_") or node.name in {"async_init", "close"}
                ):
                    names.add(node.name)
    return names


@contextmanager
def _route_server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()

    class Handler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode() if length else ""
            path = urlsplit(self.path).path
            if path == "/api/v3/time" and self.command == "GET" and not self.path.count("?"):
                payload: object = {"serverTime": int(time.time() * 1000)}
                # Clock-sync requests issued by the signer are not endpoint calls.
                received.put(
                    {"method": self.command, "path": self.path, "body": body, "sync": True}
                )
            else:
                payload = (
                    {"success": True, "code": 0, "data": []} if path.startswith("/api/v1/") else {}
                )
                received.put(
                    {
                        "method": self.command,
                        "path": self.path,
                        "body": body,
                        "sync": False,
                        "spot_key": self.headers.get("X-MEXC-APIKEY"),
                        "contract_key": self.headers.get("ApiKey"),
                        "contract_signature": self.headers.get("Signature"),
                        "contract_timestamp": self.headers.get("Request-Time"),
                    }
                )
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = _handle  # noqa: N815
        do_POST = _handle  # noqa: N815
        do_PUT = _handle  # noqa: N815
        do_DELETE = _handle  # noqa: N815

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True
    )
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "api_key": "api-key",
        "api_secret": "api-secret",
        "base_url": base_url,
        "contract_base_url": base_url,
        "preload_product_table": False,
    }


def _endpoint_requests(received: queue.Queue[dict[str, Any]]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    while not received.empty():
        requests.append(received.get_nowait())
    return requests


def _assert_route(requests: list[dict[str, Any]], method_name: str) -> None:
    _kwargs, http_method, path, signed = CASES[method_name]
    if method_name == "get_spot_time":
        endpoint = [request for request in requests if request["path"] == path]
    else:
        endpoint = [request for request in requests if not request["sync"]]
    assert len(endpoint) == 1, (method_name, requests)
    request = endpoint[0]
    from tests.unit.wire_contracts import assert_wire_contract
    assert_wire_contract("mexc", method_name, request)
    assert request["method"] == http_method, method_name
    assert urlsplit(request["path"]).path == path, method_name
    if method_name in COMPLETION_BY_NAME:
        case = COMPLETION_BY_NAME[method_name]
        encoded = urlsplit(request["path"]).query
        if path.startswith("/api/v3/"):
            fields = dict(parse_qsl(encoded))
            signature = fields.pop("signature")
            assert int(fields.pop("timestamp")) > 0
            assert fields == {key: str(value) for key, value in case["wire"].items()}
            unsigned = "&".join(
                part for part in encoded.split("&") if not part.startswith("signature=")
            )
            assert (
                signature == hmac.new(b"api-secret", unsigned.encode(), hashlib.sha256).hexdigest()
            )
            assert request["body"] == ""
        else:
            if http_method == "POST":
                assert json.loads(request["body"]) == case["wire"]
                assert encoded == ""
            else:
                assert dict(parse_qsl(encoded)) == case["wire"]
                assert request["body"] == ""
            payload = "api-key" + request["contract_timestamp"] + (request["body"] or encoded)
            assert (
                request["contract_signature"]
                == hmac.new(b"api-secret", payload.encode(), hashlib.sha256).hexdigest()
            )
    if not signed or method_name == "get_spot_time":
        return
    if path.startswith("/api/v3/"):
        assert request["spot_key"] == "api-key", method_name
        query = dict(parse_qsl(urlsplit(request["path"]).query))
        query.update(dict(parse_qsl(request["body"])))
        assert "signature" in query, method_name
        assert "timestamp" in query, method_name
    else:
        assert request["contract_key"] == "api-key", method_name
        assert request["contract_signature"], method_name


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_every_mexc_wrapper_has_a_route_case(mode: str) -> None:
    assert _wrapper_names(mode) == set(CASES)


@pytest.mark.parametrize("method_name", sorted(CASES))
def test_sync_mexc_wrapper_hits_official_route(method_name: str) -> None:
    from dcex.mexc.client import Client

    kwargs = CASES[method_name][0]
    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            getattr(client, method_name)(**kwargs)
        finally:
            client.close()
        requests = _endpoint_requests(received)
    _assert_route(requests, method_name)


@pytest.mark.asyncio
@pytest.mark.parametrize("method_name", sorted(CASES))
async def test_async_mexc_wrapper_hits_official_route(method_name: str) -> None:
    from dcex.async_support.mexc.client import Client

    kwargs = CASES[method_name][0]
    with _route_server() as (base_url, received):
        client = await Client(**_client_kwargs(base_url)).async_init()
        try:
            await getattr(client, method_name)(**kwargs)
        finally:
            await client.close()
        requests = _endpoint_requests(received)
    _assert_route(requests, method_name)


def _single_request(method_name: str, **kwargs: Any) -> dict[str, Any]:
    from dcex.mexc.client import Client

    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            getattr(client, method_name)(**kwargs)
        finally:
            client.close()
        requests = [request for request in _endpoint_requests(received) if not request["sync"]]
    assert len(requests) == 1
    return requests[0]


def test_mexc_spot_post_only_order_uses_limit_maker() -> None:
    request = _single_request(
        "place_spot_post_only_limit_buy_order",
        product_symbol=SYMBOL,
        quantity="0.5",
        price="100",
    )
    fields = dict(parse_qsl(urlsplit(request["path"]).query))
    fields.update(dict(parse_qsl(request["body"])))
    assert fields["symbol"] == "BTCUSDT"
    assert fields["side"] == "BUY"
    assert fields["type"] == "LIMIT_MAKER"
    assert fields["quantity"] == "0.5"
    assert fields["price"] == "100"


def test_mexc_contract_limit_order_json_body_matches_docs() -> None:
    request = _single_request(
        "place_contract_limit_sell_order",
        product_symbol=SWAP,
        price="100",
        vol=2,
        leverage=5,
    )
    body = json.loads(request["body"])
    assert body["symbol"] == "BTC_USDT"
    assert int(body["type"]) == 1
    assert int(body["side"]) in {2, 3}
    assert str(body["price"]) == "100"
    assert str(body["vol"]) == "2"
    assert int(body["leverage"]) == 5


def test_mexc_contract_cancel_uses_json_array_body() -> None:
    request = _single_request("cancel_contract_orders", orders=["11", "12"])
    assert json.loads(request["body"]) == ["11", "12"]


_OPENING_ORDER_WRAPPERS: dict[str, dict[str, Any]] = {
    "place_contract_order": {"side": 1, "type_": 5, "openType": 2, "vol": 1},
    "place_contract_limit_order": {"side": 1, "price": "1", "vol": 1},
    "place_contract_limit_buy_order": {"price": "1", "vol": 1},
    "place_contract_limit_sell_order": {"price": "1", "vol": 1},
    "place_contract_post_only_order": {"side": 3, "price": "1", "vol": 1},
    "place_contract_post_only_buy_order": {"price": "1", "vol": 1},
    "place_contract_post_only_sell_order": {"price": "1", "vol": 1},
    "place_contract_market_order": {"side": 3, "vol": 1},
    "place_contract_market_buy_order": {"vol": 1},
    "place_contract_market_sell_order": {"vol": 1},
}


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("method_name", sorted(_OPENING_ORDER_WRAPPERS))
def test_mexc_contract_order_wrappers_have_no_leverage_default(mode: str, method_name: str) -> None:
    import inspect

    if mode == "sync":
        from dcex.mexc.client import Client
    else:
        from dcex.async_support.mexc.client import Client
    parameter = inspect.signature(getattr(Client, method_name)).parameters["leverage"]
    assert parameter.default is None


@pytest.mark.parametrize("method_name", sorted(_OPENING_ORDER_WRAPPERS))
def test_mexc_contract_opening_order_without_leverage_is_rejected(method_name: str) -> None:
    from dcex.mexc.client import Client

    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            with pytest.raises(Exception, match="leverage"):
                getattr(client, method_name)(
                    product_symbol=SWAP, **_OPENING_ORDER_WRAPPERS[method_name]
                )
        finally:
            client.close()
        requests = [request for request in _endpoint_requests(received) if not request["sync"]]
    assert requests == []


def test_mexc_contract_closing_order_omits_leverage() -> None:
    request = _single_request("place_contract_market_order", product_symbol=SWAP, side=4, vol=1)
    body = json.loads(request["body"])
    assert int(body["side"]) == 4
    assert "leverage" not in body


def test_mexc_contract_trailing_orders_send_comma_separated_states() -> None:
    # Requires the rebuilt native extension (Rust joins JSON arrays with commas).
    request = _single_request("get_contract_trailing_orders", states=[0, 1])
    assert dict(parse_qsl(urlsplit(request["path"]).query))["states"] == "0,1"


@pytest.mark.parametrize(
    "method",
    ["cancel_contract_batch_orders_by_external_id", "get_contract_batch_orders_by_external_id"],
)
def test_external_order_batches_keep_root_array_and_each_symbol(method: str) -> None:
    request = _single_request(
        method,
        orders=[
            {"product_symbol": "BTC_USDT", "externalOid": "001"},
            {"product_symbol": "ETH_USDT", "externalOid": "002"},
        ],
    )
    assert json.loads(request["body"]) == [
        {"symbol": "BTC_USDT", "externalOid": "001"},
        {"symbol": "ETH_USDT", "externalOid": "002"},
    ]
