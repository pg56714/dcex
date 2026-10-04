"""
Offline route coverage for every Bitget REST wrapper (sync and async).

Each public wrapper method is called through the real Python client, the PyO3
bridge and the Rust dispatcher against a local HTTP server; the recorded HTTP
method and path must match the official Bitget API docs.
"""

import ast
import asyncio
import inspect
import json
import queue
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from scripts.build_bitget_wrappers import snake

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
WRAPPER_FILES = (
    "_withdrawals_http.py",
    "_transfers_http.py",
    "_batch_http.py",
    "_account_http.py",
    "_earn_http.py",
    "_market_http.py",
    "_trade_http.py",
)
WRAPPER_FILES += tuple(
    str(p.relative_to(ROOT / "dcex/bitget"))
    for p in sorted((ROOT / "dcex/bitget/_generated").glob("*_http.py"))
)

PLACE_SPOT = ("POST", "/api/v2/spot/trade/place-order")
PLACE_FUTURES = ("POST", "/api/v2/mix/order/place-order")

# Python wrapper name -> (HTTP method, documented path).
ROUTES: dict[str, tuple[str, str]] = {
    "get_futures_symbol_price": ("GET", "/api/v2/mix/market/symbol-price"),
    "modify_uta_order": ("POST", "/api/v3/trade/modify-order"),
    "cancel_uta_orders_by_symbol": ("POST", "/api/v3/trade/cancel-symbol-order"),
    "set_uta_cancel_countdown": ("POST", "/api/v3/trade/countdown-cancel-all"),
    "close_uta_positions": ("POST", "/api/v3/trade/close-positions"),
    "get_uta_position_history": ("GET", "/api/v3/position/history-position"),
    "adjust_uta_position_margin": ("POST", "/api/v3/account/set-margin"),
    "get_uta_financial_records": ("GET", "/api/v3/account/financial-records"),
    "get_uta_open_interest": ("GET", "/api/v3/market/open-interest"),
    "get_uta_current_funding_rate": ("GET", "/api/v3/market/current-fund-rate"),
    # Classic spot market data.
    "get_spot_coins": ("GET", "/api/v2/spot/public/coins"),
    "get_spot_market_trades": ("GET", "/api/v2/spot/market/fills-history"),
    # Classic futures market data.
    # UTA / Reality market data.
    "get_uta_instruments": ("GET", "/api/v3/market/instruments"),
    "get_uta_tickers": ("GET", "/api/v3/market/tickers"),
    "get_uta_orderbook": ("GET", "/api/v3/market/orderbook"),
    "get_uta_public_fills": ("GET", "/api/v3/market/fills"),
    "get_uta_kline": ("GET", "/api/v3/market/candles"),
    "get_uta_history_kline": ("GET", "/api/v3/market/history-candles"),
    "get_uta_liquidations": ("GET", "/api/v3/market/liquidations"),
    "get_reality_stock_info": ("GET", "/api/v3/reality/market/stock-info"),
    "get_reality_market_states": ("GET", "/api/v3/reality/market/states"),
    "get_reality_market_calendar": ("GET", "/api/v3/reality/market/calendar"),
    # Account, fees and transfers.
    "get_uta_account_assets": ("GET", "/api/v3/account/assets"),
    "get_reality_orderbook": ("GET", "/api/v3/account/reality-orderbook"),
    "get_reality_fills": ("GET", "/api/v3/account/reality-fills"),
    "get_uta_account_info": ("GET", "/api/v3/account/info"),
    "get_uta_all_fee_rates": ("GET", "/api/v3/account/all-fee-rate"),
    "get_uta_loan_data": ("GET", "/api/v3/trade/loan-data"),
    "get_uta_collateral_type": ("GET", "/api/v3/account/collateral-type"),
    "get_uta_custom_collateral_coins": ("GET", "/api/v3/account/custom-collateral-coins"),
    "get_uta_pre_set_leverage": ("GET", "/api/v3/account/pre-set-leverage"),
    "set_uta_leverage": ("POST", "/api/v3/account/set-leverage"),
    "set_uta_hold_mode": ("POST", "/api/v3/account/set-hold-mode"),
    # Crypto loans / UTA liability.
    "get_crypto_loan_coins": ("GET", "/api/v3/loan/coins"),
    "get_crypto_loan_interest": ("GET", "/api/v3/loan/interest"),
    "borrow_crypto_loan": ("POST", "/api/v3/loan/borrow"),
    "get_crypto_loan_ongoing": ("GET", "/api/v3/loan/borrow-ongoing"),
    "get_crypto_loan_borrow_history": ("GET", "/api/v3/loan/borrow-history"),
    "repay_crypto_loan": ("POST", "/api/v3/loan/repay"),
    "get_crypto_loan_repay_history": ("GET", "/api/v3/loan/repay-history"),
    "revise_crypto_loan_pledge": ("POST", "/api/v3/loan/revise-pledge"),
    "get_crypto_loan_pledge_history": ("GET", "/api/v3/loan/pledge-rate-history"),
    "get_crypto_loan_liquidations": ("GET", "/api/v3/loan/reduces"),
    "get_crypto_loan_debts": ("GET", "/api/v3/loan/debts"),
    "repay_uta_liability": ("POST", "/api/v3/account/repay"),
    # Earn.
    "get_elite_earn_products": ("GET", "/api/v3/earn/elite-product"),
    "get_elite_earn_subscription_info": ("GET", "/api/v3/earn/elite-subscribe-info"),
    "subscribe_elite_earn": ("POST", "/api/v3/earn/elite-subscribe"),
    "get_elite_earn_subscription_result": ("GET", "/api/v3/earn/elite-subscribe-result"),
    "get_elite_earn_redemption_info": ("GET", "/api/v3/earn/elite-redeem-info"),
    "redeem_elite_earn": ("POST", "/api/v3/earn/elite-redeem"),
    "get_elite_earn_assets": ("GET", "/api/v3/earn/elite-assets"),
    "get_elite_earn_records": ("GET", "/api/v3/earn/elite-records"),
    # Classic spot trading.
    # UTA trading.
    "place_uta_order": ("POST", "/api/v3/trade/place-order"),
    "place_reality_order": ("POST", "/api/v3/trade/place-reality-order"),
    "place_uta_batch_orders": ("POST", "/api/v3/trade/place-batch"),
    "cancel_uta_order": ("POST", "/api/v3/trade/cancel-order"),
    "cancel_reality_order": ("POST", "/api/v3/trade/cancel-reality-order"),
    "cancel_uta_batch_orders": ("POST", "/api/v3/trade/cancel-batch"),
    "get_uta_order": ("GET", "/api/v3/trade/order-info"),
    "get_uta_open_orders": ("GET", "/api/v3/trade/unfilled-orders"),
    "get_uta_history_orders": ("GET", "/api/v3/trade/history-orders"),
    "get_uta_fills": ("GET", "/api/v3/trade/fills"),
    "get_uta_positions": ("GET", "/api/v3/position/current-position"),
    "place_uta_strategy_order": ("POST", "/api/v3/trade/place-strategy-order"),
    "modify_uta_strategy_order": ("POST", "/api/v3/trade/modify-strategy-order"),
    "cancel_uta_strategy_order": ("POST", "/api/v3/trade/cancel-strategy-order"),
    "get_uta_unfilled_strategy_orders": ("GET", "/api/v3/trade/unfilled-strategy-orders"),
    "get_uta_history_strategy_orders": ("GET", "/api/v3/trade/history-strategy-orders"),
    # Classic futures trading.
}

PUBLIC_METHODS = {
    name
    for name in ROUTES
    if name.startswith(("get_spot_", "get_futures_", "get_uta_", "get_reality_"))
    and name
    not in {
        "get_uta_account_assets",
        "get_uta_account_info",
        "get_uta_all_fee_rates",
        "get_uta_loan_data",
        "get_uta_collateral_type",
        "get_uta_custom_collateral_coins",
        "get_uta_pre_set_leverage",
        "get_uta_order",
        "get_uta_open_orders",
        "get_uta_history_orders",
        "get_uta_fills",
        "get_uta_positions",
        "get_uta_unfilled_strategy_orders",
        "get_uta_history_strategy_orders",
        "get_reality_orderbook",
        "get_reality_fills",
    }
}

PUBLIC_METHODS.difference_update(
    {
        "adjust_uta_position_margin",
        "close_uta_positions",
        "get_uta_position_history",
        "cancel_uta_orders_by_symbol",
        "modify_uta_order",
        "get_uta_financial_records",
        "set_uta_cancel_countdown",
    }
)

# Sample values for required wrapper parameters, keyed by parameter name.
VALUES: dict[str, Any] = {
    "product_symbol": "BTC-USDT-SWAP",
    "category": "USDT-FUTURES",
    "side": "buy",
    "orderType": "limit",
    "size": "1",
    "qty": "1",
    "price": "1",
    "granularity": "1min",
    "interval": "1m",
    "marginMode": "crossed",
    "orderList": [{"size": "1", "side": "buy", "orderType": "limit"}],
    "coin": "USDT",
    "amount": "1",
    "fromType": "spot",
    "toType": "usdt_futures",
    "startTime": 1690000000000,
    "endTime": 1700000000000,
    "leverage": "5",
    "posMode": "one_way_mode",
    "holdMode": "one_way_mode",
    "productId": "p1",
    "periodType": "flexible",
    "productSubId": "s1",
    "redeemType": "standard",
    "receiveAccount": "spot",
    "type": "interest",
    "loanCoin": "USDT",
    "pledgeCoin": "BTC",
    "daily": "SEVEN",
    "pledgeAmount": "1",
    "orderId": "1",
    "repayAll": "yes",
    "reviseType": "IN",
    "repayableCoinList": ["USDT"],
    "paymentCoinList": ["USDT"],
}

# Optional parameters that the documented endpoint requires.
EXTRA: dict[str, dict[str, Any]] = {
    "get_uta_order": {"orderId": "1"},
    "place_uta_batch_orders": {
        "order_list": [
            {
                "category": "SPOT",
                "symbol": "BTCUSDT",
                "side": "buy",
                "orderType": "limit",
                "qty": "1",
                "price": "1",
            }
        ]
    },
    "cancel_uta_order": {"orderId": "1"},
    "cancel_reality_order": {"orderId": "1"},
    "cancel_uta_strategy_order": {"orderId": "1"},
    "modify_uta_strategy_order": {"orderId": "1"},
    "borrow_crypto_loan": {"pledgeAmount": "1"},
}


CONTROL_CASES = [
    (
        "get_futures_symbol_price",
        {"product_symbol": "BTC-USDT-SWAP", "product_type": "USDT-FUTURES"},
        "GET",
        "/api/v2/mix/market/symbol-price",
        True,
        {"symbol": "BTCUSDT", "productType": "USDT-FUTURES"},
    ),
    (
        "modify_uta_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "category": "USDT-FUTURES",
            "order_id": "123",
            "qty": "2",
            "request_id": 123456789012345678,
            "take_profit": "0",
            "stop_loss": "0",
        },
        "POST",
        "/api/v3/trade/modify-order",
        False,
        {
            "symbol": "BTCUSDT",
            "category": "USDT-FUTURES",
            "orderId": "123",
            "qty": "2",
            "requestId": 123456789012345678,
            "takeProfit": "0",
            "stopLoss": "0",
        },
    ),
    (
        "cancel_uta_orders_by_symbol",
        {"category": "USDT-FUTURES"},
        "POST",
        "/api/v3/trade/cancel-symbol-order",
        False,
        {"category": "USDT-FUTURES"},
    ),
    (
        "set_uta_cancel_countdown",
        {"countdown": "10"},
        "POST",
        "/api/v3/trade/countdown-cancel-all",
        False,
        {"countdown": "10"},
    ),
    (
        "close_uta_positions",
        {"category": "USDT-FUTURES", "all_symbols": True},
        "POST",
        "/api/v3/trade/close-positions",
        False,
        {"category": "USDT-FUTURES"},
    ),
    (
        "get_uta_position_history",
        {"category": "USDT-FUTURES"},
        "GET",
        "/api/v3/position/history-position",
        False,
        {"category": "USDT-FUTURES"},
    ),
    (
        "adjust_uta_position_margin",
        {
            "category": "USDT-FUTURES",
            "product_symbol": "BTC-USDT-SWAP",
            "pos_side": "long",
            "operation": "add",
            "amount": "1",
        },
        "POST",
        "/api/v3/account/set-margin",
        False,
        {
            "category": "USDT-FUTURES",
            "symbol": "BTCUSDT",
            "posSide": "long",
            "operation": "add",
            "amount": "1",
        },
    ),
    (
        "get_uta_financial_records",
        {"category": "USDT-FUTURES"},
        "GET",
        "/api/v3/account/financial-records",
        False,
        {"category": "USDT-FUTURES"},
    ),
    (
        "get_uta_open_interest",
        {"category": "USDT-FUTURES"},
        "GET",
        "/api/v3/market/open-interest",
        True,
        {"category": "USDT-FUTURES"},
    ),
    (
        "get_uta_current_funding_rate",
        {"category": "USDT-FUTURES"},
        "GET",
        "/api/v3/market/current-fund-rate",
        True,
        {"category": "USDT-FUTURES"},
    ),
]
CONTROL_CASES.extend(
    [
        (
            "get_futures_trade_history",
            {"product_symbol": "BTC-USDT-SWAP", "product_type": "USDT-FUTURES"},
            "GET",
            "/api/v2/mix/market/fills-history",
            True,
            {"symbol": "BTCUSDT", "productType": "USDT-FUTURES"},
        ),
        (
            "get_futures_index_candle_history",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "product_type": "USDT-FUTURES",
                "granularity": "1m",
            },
            "GET",
            "/api/v2/mix/market/history-index-candles",
            True,
            {"symbol": "BTCUSDT", "productType": "USDT-FUTURES", "granularity": "1m"},
        ),
        (
            "get_futures_mark_candle_history",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "product_type": "USDT-FUTURES",
                "granularity": "1m",
            },
            "GET",
            "/api/v2/mix/market/history-mark-candles",
            True,
            {"symbol": "BTCUSDT", "productType": "USDT-FUTURES", "granularity": "1m"},
        ),
        (
            "get_futures_next_funding_time",
            {"product_symbol": "BTC-USDT-SWAP", "product_type": "USDT-FUTURES"},
            "GET",
            "/api/v2/mix/market/funding-time",
            True,
            {"symbol": "BTCUSDT", "productType": "USDT-FUTURES"},
        ),
        (
            "get_futures_interest_exchange_rates",
            {},
            "GET",
            "/api/v2/mix/market/exchange-rate",
            True,
            {},
        ),
        (
            "get_futures_interest_rate_history",
            {"coin": "USDT"},
            "GET",
            "/api/v2/mix/market/union-interest-rate-history",
            True,
            {"coin": "USDT"},
        ),
        ("get_futures_vip_fee_rates", {}, "GET", "/api/v2/mix/market/vip-fee-rate", True, {}),
        (
            "get_uta_funding_rate_history",
            {"category": "USDT-FUTURES", "product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/history-fund-rate",
            True,
            {"category": "USDT-FUTURES", "symbol": "BTCUSDT"},
        ),
        (
            "get_uta_index_components",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/index-components",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_margin_loan_rates",
            {"coin": "USDT"},
            "GET",
            "/api/v3/market/margin-loans",
            True,
            {"coin": "USDT"},
        ),
        (
            "get_uta_position_tiers",
            {"category": "USDT-FUTURES"},
            "GET",
            "/api/v3/market/position-tier",
            True,
            {"category": "USDT-FUTURES"},
        ),
        (
            "get_uta_open_interest_limit",
            {"category": "USDT-FUTURES"},
            "GET",
            "/api/v3/market/oi-limit",
            True,
            {"category": "USDT-FUTURES"},
        ),
        ("get_uta_discount_rates", {}, "GET", "/api/v3/market/discount-rate", True, {}),
        (
            "get_uta_rpi_orderbook",
            {"category": "USDT-FUTURES", "product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/rpi-orderbook",
            True,
            {"category": "USDT-FUTURES", "symbol": "BTCUSDT"},
        ),
        ("get_uta_rpi_symbols", {}, "GET", "/api/v3/market/rpi-symbols", True, {}),
        ("get_uta_funding_assets", {}, "GET", "/api/v3/account/funding-assets", False, {}),
        (
            "get_uta_funding_records",
            {},
            "GET",
            "/api/v3/account/funding-financial-records",
            False,
            {},
        ),
        (
            "get_uta_fee_rate",
            {"product_symbol": "BTC-USDT-SWAP", "category": "USDT-FUTURES"},
            "GET",
            "/api/v3/account/fee-rate",
            False,
            {"symbol": "BTCUSDT", "category": "USDT-FUTURES"},
        ),
        (
            "get_uta_max_transferable",
            {"coin": "USDT"},
            "GET",
            "/api/v3/account/max-transferable",
            False,
            {"coin": "USDT"},
        ),
        (
            "set_uta_collateral_type",
            {"collateral_type": "all"},
            "POST",
            "/api/v3/account/set-collateral-type",
            False,
            {"collateralType": "all"},
        ),
        ("get_uta_settings", {}, "GET", "/api/v3/account/settings", False, {}),
        ("get_uta_delta_info", {}, "GET", "/api/v3/account/delta-info", False, {}),
        ("get_uta_repayable_coins", {}, "GET", "/api/v3/account/repayable-coins", False, {}),
        ("get_uta_payment_coins", {}, "GET", "/api/v3/account/payment-coins", False, {}),
        (
            "borrow_uta_asset",
            {"coin": "USDT", "amount": "1"},
            "POST",
            "/api/v3/account/borrow",
            False,
            {"coin": "USDT", "amount": "1"},
        ),
        (
            "get_uta_max_borrowable",
            {"coin": "USDT"},
            "GET",
            "/api/v3/account/max-borrowable",
            False,
            {"coin": "USDT"},
        ),
        (
            "get_uta_account_open_interest_limit",
            {"product_symbol": "BTC-USDT-SWAP", "category": "USDT-FUTURES"},
            "GET",
            "/api/v3/account/open-interest-limit",
            False,
            {"symbol": "BTCUSDT", "category": "USDT-FUTURES"},
        ),
        (
            "get_uta_transferable_coins",
            {"from_type": "spot", "to_type": "spot"},
            "GET",
            "/api/v3/account/transferable-coins",
            False,
            {"fromType": "spot", "toType": "spot"},
        ),
        (
            "get_uta_max_open_available",
            {
                "category": "USDT-FUTURES",
                "product_symbol": "BTC-USDT-SWAP",
                "order_type": "limit",
                "side": "buy",
                "price": "100",
            },
            "POST",
            "/api/v3/account/max-open-available",
            False,
            {
                "category": "USDT-FUTURES",
                "symbol": "BTCUSDT",
                "orderType": "limit",
                "side": "buy",
                "price": "100",
            },
        ),
        (
            "get_uta_position_transfer_history",
            {"category": "USDT-FUTURES"},
            "GET",
            "/api/v3/account/move-position-history",
            False,
            {"category": "USDT-FUTURES"},
        ),
        (
            "set_uta_repay_mode",
            {"repay_mode": "manual"},
            "POST",
            "/api/v3/account/set-repay-mode",
            False,
            {"repayMode": "manual"},
        ),
        (
            "get_uta_eligible_discount_rates",
            {},
            "GET",
            "/api/v3/account/eligible-discount-rate",
            False,
            {},
        ),
        ("get_uta_eligible_loan_info", {}, "GET", "/api/v3/account/eligible-loan-info", False, {}),
        (
            "get_uta_eligible_margin_tiers",
            {},
            "GET",
            "/api/v3/account/eligible-margin-tier",
            False,
            {},
        ),
        ("get_uta_eligible_symbols", {}, "GET", "/api/v3/account/eligible-symbols", False, {}),
        ("get_uta_convert_records", {}, "GET", "/api/v3/account/convert-records", False, {}),
        (
            "set_uta_account_mode",
            {"mode": "advanced", "confirm": True},
            "POST",
            "/api/v3/account/adjust-account-mode",
            False,
            {"mode": "advanced"},
        ),
        ("get_uta_adl_rank", {}, "GET", "/api/v3/position/adlRank", False, {}),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
PUBLIC_METHODS.update(name for name, _, _, _, public, _ in CONTROL_CASES if public)
PUBLIC_METHODS.difference_update(name for name, _, _, _, public, _ in CONTROL_CASES if not public)
CONTROL_CASES.extend(
    [
        (
            "modify_uta_batch_orders",
            {
                "orders": [
                    {
                        "product_symbol": "BTC-USDT-SWAP",
                        "category": "USDT-FUTURES",
                        "orderId": "123",
                        "qty": "2",
                        "requestId": 123456789012345678,
                    }
                ]
            },
            "POST",
            "/api/v3/trade/batch-modify-order",
            False,
            [
                {
                    "symbol": "BTCUSDT",
                    "category": "USDT-FUTURES",
                    "orderId": "123",
                    "qty": "2",
                    "requestId": 123456789012345678,
                }
            ],
        ),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
CONTROL_CASES.extend(
    [
        (
            "transfer_uta_account",
            {"from_type": "spot", "to_type": "uta", "amount": "1", "coin": "USDT"},
            "POST",
            "/api/v3/account/transfer",
            False,
            {"fromType": "spot", "toType": "uta", "amount": "1", "coin": "USDT"},
        ),
        (
            "transfer_uta_sub_to_master",
            {"from_type": "spot", "to_type": "uta", "amount": "1", "coin": "USDT"},
            "POST",
            "/api/v3/account/sub-master-transfer",
            False,
            {"fromType": "spot", "toType": "uta", "amount": "1", "coin": "USDT"},
        ),
        (
            "transfer_uta_sub_account",
            {
                "from_type": "spot",
                "to_type": "uta",
                "amount": "1",
                "coin": "USDT",
                "from_user_id": "1",
                "to_user_id": "2",
                "client_oid": "transfer-123",
            },
            "POST",
            "/api/v3/account/sub-transfer",
            False,
            {
                "fromType": "spot",
                "toType": "uta",
                "amount": "1",
                "coin": "USDT",
                "fromUserId": "1",
                "toUserId": "2",
                "clientOid": "transfer-123",
            },
        ),
        (
            "get_uta_sub_account_transfer_records",
            {},
            "GET",
            "/api/v3/account/sub-transfer-record",
            False,
            {},
        ),
        ("get_uta_sub_accounts", {}, "GET", "/api/v3/user/sub-list", False, {}),
        ("get_uta_sub_account_assets", {}, "GET", "/api/v3/account/sub-unified-assets", False, {}),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
PUBLIC_METHODS.update(name for name, _, _, _, public, _ in CONTROL_CASES if public)
PUBLIC_METHODS.difference_update(name for name, _, _, _, public, _ in CONTROL_CASES if not public)
CONTROL_CASES.extend(
    [
        (
            "get_uta_strategy_sub_orders",
            {"order_id": "123"},
            "GET",
            "/api/v3/trade/strategy-sub-orders",
            False,
            {"orderId": "123"},
        ),
        (
            "get_uta_deposit_records",
            {"start_time": 1700000000000, "end_time": 1700000001000},
            "GET",
            "/api/v3/account/deposit-records",
            False,
            {"startTime": "1700000000000", "endTime": "1700000001000"},
        ),
        ("get_server_time", {}, "GET", "/api/v2/public/time", True, {}),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
PUBLIC_METHODS.update(name for name, _, _, _, public, _ in CONTROL_CASES if public)
PUBLIC_METHODS.difference_update(name for name, _, _, _, public, _ in CONTROL_CASES if not public)
CONTROL_CASES.extend(
    [
        (
            "set_uta_fee_deduction",
            {"deduct": "on"},
            "POST",
            "/api/v3/account/switch-deduct",
            False,
            {"deduct": "on"},
        ),
        ("get_uta_fee_deduction", {}, "GET", "/api/v3/account/deduct-info", False, {}),
        ("switch_to_classic_account", {"confirm": True}, "POST", "/api/v3/account/switch", False, {}),
        ("get_account_switch_status", {}, "GET", "/api/v3/account/switch-status", False, {}),
        (
            "set_uta_deposit_account",
            {"coin": "USDT", "account_type": "unified"},
            "POST",
            "/api/v3/account/deposit-account",
            False,
            {"coin": "USDT", "accountType": "unified"},
        ),
        (
            "create_uta_sub_account",
            {"username": "trader"},
            "POST",
            "/api/v3/user/create-sub",
            False,
            {"username": "trader"},
        ),
        (
            "get_uta_cash_dividend_records",
            {"product_symbol": "BTC-USDT-SWAP", "type_": "pending"},
            "GET",
            "/api/v3/market/cash-dividend-records",
            True,
            {"symbol": "BTCUSDT", "type": "pending"},
        ),
        (
            "get_uta_risk_reserve",
            {"category": "USDT-FUTURES", "product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/risk-reserve",
            True,
            {"category": "USDT-FUTURES", "symbol": "BTCUSDT"},
        ),
        (
            "get_uta_all_risk_reserves",
            {"category": "USDT-FUTURES"},
            "GET",
            "/api/v3/market/risk-reserve-all",
            True,
            {"category": "USDT-FUTURES"},
        ),
        (
            "get_uta_hourly_risk_reserve",
            {"category": "USDT-FUTURES", "product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/risk-reserve-hour",
            True,
            {"category": "USDT-FUTURES", "symbol": "BTCUSDT"},
        ),
        ("get_uta_split_records", {}, "GET", "/api/v3/market/split-records", True, {}),
        (
            "get_uta_futures_long_short_ratio",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/futures-account-long-short",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_spot_whale_flow",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/spot-whale-flow",
            True,
            {"symbol": "BTCUSDT"},
        ),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
PUBLIC_METHODS.update(name for name, _, _, _, public, _ in CONTROL_CASES if public)
PUBLIC_METHODS.difference_update(name for name, _, _, _, public, _ in CONTROL_CASES if not public)
CONTROL_CASES.extend(
    [
        (
            "get_uta_deposit_address",
            {"coin": "USDT"},
            "GET",
            "/api/v3/account/deposit-address",
            False,
            {"coin": "USDT"},
        ),
        (
            "get_uta_sub_deposit_address",
            {"sub_uid": "2", "coin": "USDT"},
            "GET",
            "/api/v3/account/sub-deposit-address",
            False,
            {"subUid": "2", "coin": "USDT"},
        ),
        (
            "get_uta_sub_deposit_records",
            {"sub_uid": "2", "start_time": 1700000000000, "end_time": 1700000001000},
            "GET",
            "/api/v3/account/sub-deposit-records",
            False,
            {"subUid": "2", "startTime": "1700000000000", "endTime": "1700000001000"},
        ),
        (
            "get_uta_rate_limit_quota",
            {"category": "spot"},
            "GET",
            "/api/v3/user/rate-limit-quota",
            False,
            {"category": "spot"},
        ),
        (
            "uta_set_rate_limit_quota",
            {"category": "spot", "uids": ["2"], "quota": "5"},
            "POST",
            "/api/v3/user/set-rate-limit-quota",
            False,
            {"category": "spot", "uids": ["2"], "quota": "5"},
        ),
        (
            "get_uta_small_assets_history",
            {},
            "GET",
            "/api/v3/convert/small-assets-history",
            False,
            {},
        ),
        ("get_uta_small_assets", {}, "GET", "/api/v3/convert/small-assets", False, {}),
        (
            "convert_uta_small_assets",
            {"from_coin_list": ["ETH"]},
            "POST",
            "/api/v3/convert/small-assets-trade",
            False,
            {"fromCoinList": ["ETH"]},
        ),
        (
            "delete_uta_subaccount",
            {"sub_uid": "2", "confirm": True},
            "POST",
            "/api/v3/user/delete-sub",
            False,
            {"subUid": "2"},
        ),
        (
            "uta_freeze_sub",
            {"sub_uid": "2", "operation": "freeze"},
            "POST",
            "/api/v3/user/freeze-sub",
            False,
            {"subUid": "2", "operation": "freeze"},
        ),
        (
            "uta_create_sub_api",
            {
                "sub_uid": "2",
                "note": "trading",
                "type_": "read_only",
                "passphrase": "Trading123",
                "permissions": ["uta_trade"],
                "ips": ["127.0.0.1"],
            },
            "POST",
            "/api/v3/user/create-sub-api",
            False,
            {
                "subUid": "2",
                "note": "trading",
                "type": "read_only",
                "passphrase": "Trading123",
                "permissions": ["uta_trade"],
                "ips": ["127.0.0.1"],
            },
        ),
        (
            "uta_update_sub_api",
            {"api_key": "api-key", "passphrase": "Trading123"},
            "POST",
            "/api/v3/user/update-sub-api",
            False,
            {"apiKey": "api-key", "passphrase": "Trading123"},
        ),
        (
            "uta_delete_sub_api",
            {"api_key": "api-key"},
            "POST",
            "/api/v3/user/delete-sub-api",
            False,
            {"apiKey": "api-key"},
        ),
        (
            "get_uta_sub_api_list",
            {"sub_uid": "2"},
            "GET",
            "/api/v3/user/sub-api-list",
            False,
            {"subUid": "2"},
        ),
        (
            "get_classic_interest_rate_record",
            {"coin": "USDT"},
            "GET",
            "/api/v2/margin/interest-rate-record",
            True,
            {"coin": "USDT"},
        ),
        ("get_classic_margin_currencies", {}, "GET", "/api/v2/margin/currencies", True, {}),
        ("get_classic_convert_currencies", {}, "GET", "/api/v2/convert/currencies", True, {}),
        (
            "get_classic_auction",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v2/spot/market/auction",
            True,
            {"symbol": "BTCUSDT"},
        ),
        ("get_classic_vip_fee_rate", {}, "GET", "/api/v2/spot/market/vip-fee-rate", True, {}),
        ("get_uta_proof_of_reserves", {}, "GET", "/api/v3/market/proof-of-reserves", True, {}),
        ("get_uta_score_weights", {}, "GET", "/api/v3/market/score-weights", True, {}),
        (
            "get_uta_fee_group",
            {"category": "USDT-FUTURES"},
            "GET",
            "/api/v3/market/fee-group",
            True,
            {"category": "USDT-FUTURES"},
        ),
        (
            "get_uta_spot_fund_flow",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/spot-fund-flow",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_spot_net_flow",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/spot-net-flow",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_margin_long_short",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/margin-long-short",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_margin_loan_growth",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/margin-loan-growth",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_margin_isolated_borrow",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/margin-isolated-borrow",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_futures_active_buy_sell",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/futures-active-buy-sell",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_futures_long_short",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/futures-long-short",
            True,
            {"symbol": "BTCUSDT"},
        ),
        (
            "get_uta_futures_position_long_short",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/api/v3/market/futures-position-long-short",
            True,
            {"symbol": "BTCUSDT"},
        ),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
PUBLIC_METHODS.update(name for name, _, _, _, public, _ in CONTROL_CASES if public)
PUBLIC_METHODS.difference_update(name for name, _, _, _, public, _ in CONTROL_CASES if not public)
CONTROL_CASES.extend(
    [
        (
            "move_uta_positions",
            {
                "from_uid": "1",
                "to_uid": "2",
                "category": "USDT-FUTURES",
                "position_list": [{"symbol": "BTCUSDT", "side": "sell", "qty": "0.01"}],
                "confirm": True,
            },
            "POST",
            "/api/v3/account/move-positions",
            False,
            {
                "fromUid": "1",
                "toUid": "2",
                "category": "USDT-FUTURES",
                "positionList": [{"symbol": "BTCUSDT", "side": "sell", "qty": "0.01"}],
            },
        ),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
CONTROL_CASES.extend(
    [
        (
            "get_uta_account_max_withdrawal",
            {"coin": "USDT"},
            "GET",
            "/api/v3/account/max-withdrawal",
            False,
            {"coin": "USDT"},
        ),
        (
            "get_uta_account_withdrawal_records",
            {"start_time": "1700000000000", "end_time": "1700000001000"},
            "GET",
            "/api/v3/account/withdrawal-records",
            False,
            {"startTime": "1700000000000", "endTime": "1700000001000"},
        ),
        (
            "get_uta_account_withdraw_address",
            {},
            "GET",
            "/api/v3/account/withdraw-address",
            False,
            {},
        ),
        (
            "get_classic_earn_loan_public_coin_infos",
            {},
            "GET",
            "/api/v2/earn/loan/public/coinInfos",
            True,
            {},
        ),
        (
            "get_classic_earn_loan_public_hour_interest",
            {"loan_coin": "BTC", "pledge_coin": "USDT", "daily": "7", "pledge_amount": "100"},
            "GET",
            "/api/v2/earn/loan/public/hour-interest",
            True,
            {"loanCoin": "BTC", "pledgeCoin": "USDT", "daily": "7", "pledgeAmount": "100"},
        ),
        (
            "uta_trade_grid_add_investment",
            {
                "category": "SPOT",
                "bot_id": "1",
                "coin": "USDT",
                "size": "100",
                "funds_source": ["uta"],
            },
            "POST",
            "/api/v3/trade/grid/add-investment",
            False,
            {
                "category": "SPOT",
                "botId": "1",
                "coin": "USDT",
                "size": "100",
                "fundsSource": ["uta"],
            },
        ),
        (
            "get_uta_trade_grid_bot_detail",
            {"bot_id": "1"},
            "GET",
            "/api/v3/trade/grid/bot-detail",
            False,
            {"botId": "1"},
        ),
        (
            "uta_trade_grid_close_bot",
            {"bot_id": "1"},
            "POST",
            "/api/v3/trade/grid/close-bot",
            False,
            {"botId": "1"},
        ),
        (
            "uta_trade_grid_create_bot",
            {
                "category": "SPOT",
                "symbol": "BTCUSDT",
                "max_price": "60000",
                "min_price": "40000",
                "grid_num": "10",
                "grid_order_mode": "arithmetic",
                "investment_amount": [{"coin": "USDT", "amount": "100"}],
                "funds_source": ["uta"],
                "slippage": "0.01",
                "auto_transfer_profits": "no",
            },
            "POST",
            "/api/v3/trade/grid/create-bot",
            False,
            {
                "category": "SPOT",
                "symbol": "BTCUSDT",
                "maxPrice": "60000",
                "minPrice": "40000",
                "gridNum": "10",
                "gridOrderMode": "arithmetic",
                "investmentAmount": [{"coin": "USDT", "amount": "100"}],
                "fundsSource": ["uta"],
                "slippage": "0.01",
                "autoTransferProfits": "no",
            },
        ),
        (
            "uta_trade_grid_create_neutral_bot",
            {
                "category": "USDT-FUTURES",
                "symbol": "BTCUSDT",
                "max_price": "60000",
                "min_price": "40000",
                "grid_num": "10",
                "grid_order_mode": "arithmetic",
                "funds_source": ["uta"],
            },
            "POST",
            "/api/v3/trade/grid/create-neutral-bot",
            False,
            {
                "category": "USDT-FUTURES",
                "symbol": "BTCUSDT",
                "maxPrice": "60000",
                "minPrice": "40000",
                "gridNum": "10",
                "gridOrderMode": "arithmetic",
                "fundsSource": ["uta"],
            },
        ),
        (
            "get_uta_trade_grid_list_details",
            {"category": "SPOT", "bot_id": "1"},
            "GET",
            "/api/v3/trade/grid/list-details",
            False,
            {"category": "SPOT", "botId": "1"},
        ),
        (
            "uta_trade_grid_modify_bot",
            {"bot_id": "1"},
            "POST",
            "/api/v3/trade/grid/modify-bot",
            False,
            {"botId": "1"},
        ),
        (
            "uta_trade_grid_modify_grid_interval",
            {
                "category": "SPOT",
                "bot_id": "1",
                "max_price": "60000",
                "min_price": "40000",
                "grid_num": "10",
            },
            "POST",
            "/api/v3/trade/grid/modify-grid-interval",
            False,
            {
                "category": "SPOT",
                "botId": "1",
                "maxPrice": "60000",
                "minPrice": "40000",
                "gridNum": "10",
            },
        ),
        (
            "uta_trade_grid_modify_neutral_bot",
            {"bot_id": "1", "category": "SPOT"},
            "POST",
            "/api/v3/trade/grid/modify-neutral-bot",
            False,
            {"botId": "1", "category": "SPOT"},
        ),
        (
            "uta_trade_grid_modify_neutral_grid_interval",
            {
                "category": "SPOT",
                "bot_id": "1",
                "max_price": "60000",
                "min_price": "40000",
                "grid_num": "10",
            },
            "POST",
            "/api/v3/trade/grid/modify-neutral-grid-interval",
            False,
            {
                "category": "SPOT",
                "botId": "1",
                "maxPrice": "60000",
                "minPrice": "40000",
                "gridNum": "10",
            },
        ),
        (
            "get_uta_trade_grid_neutral_bot_detail",
            {"bot_id": "1"},
            "GET",
            "/api/v3/trade/grid/neutral-bot-detail",
            False,
            {"botId": "1"},
        ),
        (
            "get_uta_trade_grid_neutral_list_details",
            {"category": "SPOT", "bot_id": "1"},
            "GET",
            "/api/v3/trade/grid/neutral-list-details",
            False,
            {"category": "SPOT", "botId": "1"},
        ),
        (
            "uta_trade_grid_validate_neutral",
            {
                "category": "USDT-FUTURES",
                "symbol": "BTCUSDT",
                "max_price": "60000",
                "min_price": "40000",
                "grid_num": "10",
                "grid_order_mode": "arithmetic",
            },
            "POST",
            "/api/v3/trade/grid/validate-neutral",
            False,
            {
                "category": "USDT-FUTURES",
                "symbol": "BTCUSDT",
                "maxPrice": "60000",
                "minPrice": "40000",
                "gridNum": "10",
                "gridOrderMode": "arithmetic",
            },
        ),
        (
            "uta_trade_grid_validate",
            {
                "category": "SPOT",
                "symbol": "BTCUSDT",
                "max_price": "60000",
                "min_price": "40000",
                "grid_num": "10",
                "grid_order_mode": "arithmetic",
                "investment_amount": [{"coin": "USDT", "amount": "100"}],
                "auto_transfer_profits": "no",
            },
            "POST",
            "/api/v3/trade/grid/validate",
            False,
            {
                "category": "SPOT",
                "symbol": "BTCUSDT",
                "maxPrice": "60000",
                "minPrice": "40000",
                "gridNum": "10",
                "gridOrderMode": "arithmetic",
                "investmentAmount": [{"coin": "USDT", "amount": "100"}],
                "autoTransferProfits": "no",
            },
        ),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
PUBLIC_METHODS.update(name for name, _, _, _, public, _ in CONTROL_CASES if public)
PUBLIC_METHODS.difference_update(name for name, _, _, _, public, _ in CONTROL_CASES if not public)
CONTROL_CASES.extend(
    [
        (
            "get_reality_company_overview",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/company-overview",
            True,
            {"code": "MU"},
        ),
        (
            "get_reality_valuation_indicators",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/valuation-indicators",
            True,
            {"code": "MU"},
        ),
        (
            "get_reality_earnings_forecast",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/earnings-forecast",
            True,
            {"code": "MU"},
        ),
        (
            "get_reality_suspension_resumption_info",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/suspension-resumption-info",
            True,
            {"code": "MU"},
        ),
        (
            "get_reality_dividends",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/dividends",
            True,
            {"code": "MU"},
        ),
        (
            "get_reality_share_capital_change",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/share-capital-change",
            True,
            {"code": "MU"},
        ),
        (
            "get_reality_inner_trades",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/inner-trades",
            True,
            {"code": "MU"},
        ),
        (
            "get_reality_executive_shareholdings",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/executive-shareholdings",
            True,
            {"code": "MU"},
        ),
        (
            "get_reality_sharehold_detail",
            {"code": "MU"},
            "GET",
            "/api/v3/reality/market/sharehold-detail",
            True,
            {"code": "MU"},
        ),
    ]
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
PUBLIC_METHODS.update(name for name, _, _, _, public, _ in CONTROL_CASES if public)
PUBLIC_METHODS.difference_update(name for name, _, _, _, public, _ in CONTROL_CASES if not public)
COMPLETION_CASES = json.loads(
    (Path(__file__).parents[1] / "fixtures/bitget_request_cases.json").read_text(encoding="utf-8")
)
CONTROL_CASES.extend(
    (c["method"], c["kwargs"], "POST", c["path"], False, c["body"]) for c in COMPLETION_CASES
)
ROUTES.update({name: (verb, path) for name, _, verb, path, _, _ in CONTROL_CASES})
EXTRA.update({name: kwargs for name, kwargs, *_ in CONTROL_CASES})


def _wrapper_names(mode: str) -> set[str]:
    base = ROOT / "dcex"
    if mode == "async":
        base /= "async_support"
    names: set[str] = set()
    for filename in WRAPPER_FILES:
        tree = ast.parse((base / "bitget" / filename).read_text(encoding="utf-8"))
        for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            for node in cls.body:
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and not (
                    node.name.startswith("_")
                ):
                    names.add(node.name)
                elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Name):
                    names.update(
                        target.id
                        for target in node.targets
                        if isinstance(target, ast.Name) and not target.id.startswith("_")
                    )
    return names


class _Recorder(BaseHTTPRequestHandler):
    received: "queue.Queue[dict[str, Any]]"

    def _handle(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode() if length else ""
        split = urlsplit(self.path)
        self.received.put(
            {
                "method": self.command,
                "path": split.path,
                "query": dict(parse_qsl(split.query)),
                "body": body,
                "signed": bool(self.headers.get("ACCESS-SIGN")),
                "headers": dict(self.headers),
            }
        )
        payload = json.dumps({"code": "00000", "msg": "success", "data": {}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = do_PUT = do_DELETE = _handle  # noqa: N815

    def log_message(self, _format: str, *_args: object) -> None:
        return


@pytest.fixture(scope="module")
def server() -> Iterator[tuple[str, "queue.Queue[dict[str, Any]]"]]:
    """Run a local recording HTTP server for the whole module."""
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    handler = type("Handler", (_Recorder,), {"received": received})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(
        target=httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        host, port = httpd.server_address[:2]
        yield f"http://{host}:{port}", received
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=10)


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "api_key": "api-key",
        "api_secret": "api-secret",
        "passphrase": "passphrase",
        "base_url": base_url,
        "preload_product_table": False,
    }


def _python_fields(method, values):
    """Translate wire sample names to the current Python signature."""
    parameters = inspect.signature(method).parameters
    return {
        key if key in parameters else snake(key).replace("_i_ds", "_ids"): value
        for key, value in values.items()
    }


def _kwargs(method: Any, name: str) -> dict[str, Any]:  # noqa: ANN401
    if name in {case[0] for case in CONTROL_CASES}:
        return _python_fields(method, EXTRA[name].copy())
    kwargs: dict[str, Any] = {}
    samples = _python_fields(method, VALUES)
    for parameter in inspect.signature(method).parameters.values():
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        if parameter.default is inspect.Parameter.empty:
            sample_name = parameter.name
            if sample_name not in samples:
                raise AssertionError(f"{name}: no sample value for {parameter.name}")
            kwargs[sample_name] = samples[sample_name]
    kwargs.update(EXTRA.get(name, {}))
    if name in {"cancel_uta_batch_orders"}:
        kwargs["orderList"] = [{"orderId": "123"}]
    return _python_fields(method, kwargs)


def _drain(received: "queue.Queue[dict[str, Any]]") -> None:
    while not received.empty():
        received.get_nowait()


def _assert_route(name: str, request: dict[str, Any]) -> None:
    from tests.unit.wire_contracts import assert_wire_contract

    assert_wire_contract("bitget", name, request)
    method, path = ROUTES[name]
    assert (request["method"], request["path"]) == (method, path), name
    assert request["signed"] is (name not in PUBLIC_METHODS), name
    if method == "GET":
        assert request["body"] == "", name
    else:
        json.loads(request["body"])
    if name in {c["method"] for c in COMPLETION_CASES}:
        import base64
        import hashlib
        import hmac

        headers = {key.lower(): value for key, value in request["headers"].items()}
        preimage = headers["access-timestamp"] + method + path + request["body"]
        assert (
            headers["access-sign"]
            == base64.b64encode(
                hmac.new(b"api-secret", preimage.encode(), hashlib.sha256).digest()
            ).decode()
        )
        assert request["query"] == {}
    for case_name, _, _, _, _, expected in CONTROL_CASES:
        if case_name == name:
            actual = request["query"] if method == "GET" else json.loads(request["body"])
            assert actual == expected, name


def test_route_table_matches_python_surface() -> None:
    """Every sync/async wrapper (including Earn, outside the generic suffix list) is mapped."""
    sync_names = _wrapper_names("sync")
    async_names = _wrapper_names("async")
    assert sync_names == async_names
    from tests.unit.test_bitget_schema_requests import NAMES

    assert sync_names == set(ROUTES) | NAMES


@pytest.mark.parametrize("name", sorted(ROUTES))
def test_sync_wrapper_reaches_documented_route(
    name: str, server: tuple[str, "queue.Queue[dict[str, Any]]"]
) -> None:
    """Sync wrapper -> PyO3 -> Rust reaches the documented METHOD + path."""
    from dcex.bitget.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    method = getattr(client, name)
    result = method(**_kwargs(method, name))
    assert result["code"] == "00000"
    _assert_route(name, received.get(timeout=10))


@pytest.mark.parametrize("name", sorted(ROUTES))
def test_async_wrapper_reaches_documented_route(
    name: str, server: tuple[str, "queue.Queue[dict[str, Any]]"]
) -> None:
    """Async wrapper -> PyO3 -> Rust reaches the documented METHOD + path."""
    from dcex.async_support.bitget.client import Client

    base_url, received = server
    _drain(received)

    async def call() -> Any:  # noqa: ANN401
        async with Client(**_client_kwargs(base_url)) as client:
            method = getattr(client, name)
            kwargs = _kwargs(method, name)
            return await method(**kwargs)

    result = asyncio.run(call())
    assert result["code"] == "00000"
    _assert_route(name, received.get(timeout=10))


def test_sync_client_error_surfaces_bitget_code(
    server: tuple[str, "queue.Queue[dict[str, Any]]"],
) -> None:
    """Rust-side validation errors surface before any request is sent."""
    from dcex.bitget.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    with pytest.raises(Exception, match="between 1 and 100"):
        client.get_reality_fills(product_symbol="RAAPL-USDT-SPOT", limit=101)
    assert received.empty()


def test_python_validation_rejects_ambiguous_loan_calls(
    server: tuple[str, "queue.Queue[dict[str, Any]]"],
) -> None:
    """Leverage needs a value and crypto-loan borrow needs exactly one amount (sync + async)."""
    from dcex.async_support.bitget.client import Client as AsyncClient
    from dcex.bitget.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    loan = {"loan_coin": "USDT", "pledge_coin": "BTC", "daily": "SEVEN"}
    for amounts in ({}, {"pledge_amount": "1", "loan_amount": "1"}):
        with pytest.raises(ValueError, match="exactly one of pledgeAmount or loanAmount"):
            client.borrow_crypto_loan(**loan, **amounts)

    async def call_async() -> None:
        async with AsyncClient(**_client_kwargs(base_url)) as async_client:
            for amounts in ({}, {"pledge_amount": "1", "loan_amount": "1"}):
                with pytest.raises(ValueError, match="exactly one of pledgeAmount or loanAmount"):
                    await async_client.borrow_crypto_loan(**loan, **amounts)

    asyncio.run(call_async())
    assert received.empty()


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    ("name", "kwargs", "message"),
    [
        ("set_uta_collateral_type", {"collateral_type": "custom"}, "collateralCoins"),
        ("set_uta_account_mode", {"mode": "delta", "confirm": True}, "unsupported mode"),
        (
            "set_uta_account_mode",
            {"mode": "basic", "delta_switch": "yes", "confirm": True},
            "advanced mode",
        ),
        (
            "get_futures_index_candle_history",
            {
                "product_symbol": "BTCUSDT",
                "product_type": "USDT-FUTURES",
                "granularity": "1m",
                "limit": 201,
            },
            "range",
        ),
        (
            "get_uta_funding_records",
            {"start_time": 1700000000000, "end_time": 1702678400000},
            "time range",
        ),
        (
            "transfer_uta_account",
            {"from_type": "spot", "to_type": "isolated_margin", "amount": "1", "coin": "USDT"},
            "symbol",
        ),
        ("modify_uta_batch_orders", {"orders": []}, "batch size"),
        (
            "modify_uta_batch_orders",
            {
                "orders": [
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                ]
            },
            "batch size",
        ),
        (
            "modify_uta_batch_orders",
            {
                "orders": [
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                ]
            },
            "only once",
        ),
        (
            "modify_uta_batch_orders",
            {
                "orders": [
                    {"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "1"},
                    {"symbol": "BTCUSDT", "category": "SPOT", "orderId": "456", "qty": "1"},
                ]
            },
            "same category",
        ),
        (
            "modify_uta_batch_orders",
            {
                "orders": [
                    {
                        "symbol": "BTCUSDT",
                        "category": "USDT-FUTURES",
                        "orderId": "123",
                        "qty": "1",
                        "requestId": "123",
                    }
                ]
            },
            "requestId must be a number",
        ),
        (
            "modify_uta_batch_orders",
            {
                "orders": [
                    {
                        "symbol": "BTCUSDT",
                        "category": "USDT-FUTURES",
                        "orderId": "123",
                        "qty": "1",
                        "requestId": 1000000000000000000,
                    }
                ]
            },
            "18 digits",
        ),
        (
            "modify_uta_batch_orders",
            {"orders": [{"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123"}]},
            "qty or price",
        ),
        (
            "modify_uta_order",
            {
                "product_symbol": "BTCUSDT",
                "category": "USDT-FUTURES",
                "order_id": "1",
                "qty": "1",
                "request_id": 10**18,
            },
            "18 digits",
        ),
        ("set_uta_cancel_countdown", {"countdown": "4"}, "5..=60"),
    ],
)
def test_controls_reject_invalid_requests(
    asynchronous: bool, name: str, kwargs: dict[str, Any], message: str
) -> None:
    """Invalid risk inputs fail before attempting any network request."""
    from dcex.async_support.bitget.client import Client as AsyncClient
    from dcex.bitget.client import Client

    async def invoke() -> None:
        client = AsyncClient(**_client_kwargs("http://127.0.0.1:9"))
        try:
            await client.async_init()
            with pytest.raises(Exception, match=message):
                await getattr(client, name)(**kwargs)
        finally:
            await client.close()

    if asynchronous:
        asyncio.run(invoke())
    else:
        client = Client(**_client_kwargs("http://127.0.0.1:9"))
        try:
            with pytest.raises(Exception, match=message):
                getattr(client, name)(**kwargs)
        finally:
            client.close()
