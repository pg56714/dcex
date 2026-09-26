"""
Offline end-to-end route coverage for every KuCoin Python wrapper.

Every public wrapper on the sync and async KuCoin clients (including the
``_earn_http.py`` and ``_margin_http.py`` mixins, which the shared
``ENDPOINT_FILE_SUFFIXES`` list does not pick up) is called against local HTTP
servers through the real native transport. Each case asserts the HTTP method,
the REST path from the official KuCoin API docs, and that the request reached
the right host (spot ``api.kucoin.com`` vs futures ``api-futures.kucoin.com``).
"""

# ruff: noqa: D103

from __future__ import annotations

import inspect
import json
import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
SPOT = "BTC-USDT-SPOT"
SWAP = "BTC-USDT-SWAP"


@dataclass(frozen=True)
class Case:
    """One wrapper call and the HTTP request it must produce."""

    method_name: str
    kwargs: dict[str, Any]
    route: str
    host: str = "spot"
    query: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    signed: bool = True

    @property
    def id(self) -> str:
        """Return the pytest id, disambiguating repeated method names."""
        suffix = "-".join(sorted(self.kwargs)) if self.method_name in _DUPLICATE_NAMES else ""
        return f"{self.method_name}{'-' + suffix if suffix else ''}"


_DUPLICATE_NAMES = {"get_futures_orderbook", "get_spot_orderbook"}

LIMIT = {"size": "1", "price": "100"}
FUT_LIMIT = {"size": "1", "price": "100", "leverage": 3}

CASES: tuple[Case, ...] = (
    # Market data (public).
    Case("get_spot_instrument_info", {}, "GET /api/v2/symbols", signed=False),
    Case(
        "get_spot_ticker",
        {"product_symbol": SPOT},
        "GET /api/v1/market/orderbook/level1",
        query={"symbol": "BTC-USDT"},
        signed=False,
    ),
    Case("get_spot_all_tickers", {}, "GET /api/v1/market/allTickers", signed=False),
    Case(
        "get_spot_orderbook",
        {"product_symbol": SPOT},
        "GET /api/v1/market/orderbook/level2_20",
        query={"symbol": "BTC-USDT"},
        signed=False,
    ),
    Case(
        "get_spot_orderbook",
        {"product_symbol": SPOT, "depth": 100},
        "GET /api/v1/market/orderbook/level2_100",
        query={"symbol": "BTC-USDT"},
        signed=False,
    ),
    Case(
        "get_spot_public_trades",
        {"product_symbol": SPOT},
        "GET /api/v1/market/histories",
        query={"symbol": "BTC-USDT"},
        signed=False,
    ),
    Case(
        "get_spot_kline",
        {"product_symbol": SPOT, "timeframe": "1m"},
        "GET /api/v1/market/candles",
        query={"symbol": "BTC-USDT", "type": "1min"},
        signed=False,
    ),
    Case(
        "get_futures_contracts",
        {},
        "GET /api/v1/contracts/active",
        host="futures",
        signed=False,
    ),
    Case(
        "get_futures_contract",
        {"product_symbol": SWAP},
        "GET /api/v1/contracts/XBTUSDTM",
        host="futures",
        signed=False,
    ),
    Case(
        "get_futures_ticker",
        {"product_symbol": SWAP},
        "GET /api/v1/ticker",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_futures_orderbook",
        {"product_symbol": SWAP},
        "GET /api/v1/level2/snapshot",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_futures_orderbook",
        {"product_symbol": SWAP, "depth": "100"},
        "GET /api/v1/level2/depth100",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_futures_public_trades",
        {"product_symbol": SWAP},
        "GET /api/v1/trade/history",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_futures_kline",
        {"product_symbol": SWAP, "timeframe": "1m"},
        "GET /api/v1/kline/query",
        host="futures",
        query={"symbol": "XBTUSDTM", "granularity": "1"},
        signed=False,
    ),
    Case(
        "get_futures_open_interest",
        {"product_symbol": SWAP},
        "GET /api/ua/v2/market/open-interest",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_uta_position_tiers",
        {
            "product_symbol": SWAP,
            "tradeType": "FUTURES",
            "marginMode": "CROSS",
            "data": "RISK_LIMIT",
            "accountType": "UNIFIED",
        },
        "GET /api/ua/v2/market/position-tiers",
        query={"symbol": "XBTUSDTM", "tradeType": "FUTURES"},
        signed=False,
    ),
    # Margin market data (public).
    Case("get_cross_margin_symbols", {}, "GET /api/v3/margin/symbols", signed=False),
    Case("get_isolated_margin_symbols", {}, "GET /api/v1/isolated/symbols", signed=False),
    Case(
        "get_margin_collateral_ratio",
        {},
        "GET /api/v3/margin/collateralRatio",
        signed=False,
    ),
    Case(
        "get_margin_available_inventory",
        {"currency": "USDT"},
        "GET /api/v3/margin/available-inventory",
        query={"currency": "USDT"},
        signed=False,
    ),
    Case(
        "get_margin_loan_market_interest_rate",
        {"currency": "USDT"},
        "GET /api/v3/project/marketInterestRate",
        query={"currency": "USDT"},
        signed=False,
    ),
    # Account, fees, transfers, sub-accounts.
    Case(
        "get_spot_fee_rates",
        {"product_symbol": SPOT},
        "GET /api/v1/trade-fees",
        query={"symbols": "BTC-USDT"},
    ),
    Case(
        "get_futures_fee_rates",
        {"product_symbol": SWAP},
        "GET /api/v1/trade-fees",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_uta_fee_rates",
        {"tradeType": "SPOT", "symbol": "BTC-USDT"},
        "GET /api/ua/v2/user/fee-rate",
        query={"tradeType": "SPOT", "symbol": "BTC-USDT"},
    ),
    Case(
        "get_account_balance",
        {"currency": "USDT", "type": "trade"},
        "GET /api/v1/accounts",
        query={"currency": "USDT", "type": "trade"},
    ),
    Case(
        "get_transfer_quotas",
        {"currency": "USDT", "account_type": "MAIN"},
        "GET /api/v1/accounts/transferable",
        query={"currency": "USDT", "type": "MAIN"},
    ),
    Case(
        "flex_transfer",
        {
            "currency": "USDT",
            "amount": "1",
            "fromAccountType": "MAIN",
            "toAccountType": "TRADE",
        },
        "POST /api/v3/accounts/universal-transfer",
        body={"currency": "USDT", "amount": "1", "type": "INTERNAL"},
    ),
    Case("get_subaccounts", {}, "GET /api/v2/sub/user"),
    Case(
        "get_subaccount_balance",
        {"subUserId": "123"},
        "GET /api/v1/sub-accounts/123",
    ),
    Case("get_spot_subaccount_balances", {}, "GET /api/v2/sub-accounts"),
    Case(
        "get_futures_subaccount_balances",
        {"currency": "USDT"},
        "GET /api/v1/account-overview-all",
        host="futures",
        query={"currency": "USDT"},
    ),
    Case("get_uta_subaccounts", {}, "GET /api/ua/v2/user/sub-account-list"),
    Case(
        "get_uta_subaccount_currency_assets",
        {},
        "GET /api/ua/v2/sub-account/balance",
    ),
    Case(
        "get_futures_account",
        {"currency": "USDT"},
        "GET /api/v1/account-overview",
        host="futures",
        query={"currency": "USDT"},
    ),
    Case("get_futures_positions", {}, "GET /api/v1/positions", host="futures"),
    Case(
        "get_futures_position",
        {"product_symbol": SWAP},
        "GET /api/v2/position",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_futures_position_mode",
        {},
        "GET /api/v2/position/getPositionMode",
        host="futures",
    ),
    Case(
        "get_futures_cross_margin_leverage",
        {"product_symbol": SWAP},
        "GET /api/v2/getCrossUserLeverage",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "modify_futures_cross_margin_leverage",
        {"product_symbol": SWAP, "leverage": "5"},
        "POST /api/v2/changeCrossUserLeverage",
        host="futures",
        body={"symbol": "XBTUSDTM", "leverage": "5"},
    ),
    Case("get_uta_positions", {}, "GET /api/ua/v2/unified/position/open-list"),
    Case("get_uta_account_balance", {}, "GET /api/ua/v2/unified/account/balance"),
    Case("get_uta_account_overview", {}, "GET /api/ua/v2/unified/account/overview"),
    # Earn.
    Case(
        "purchase_earn",
        {"productId": "1", "amount": "10", "accountType": "MAIN"},
        "POST /api/v1/earn/orders",
        body={"productId": "1", "amount": "10", "accountType": "MAIN"},
    ),
    Case(
        "get_earn_redeem_preview",
        {"orderId": "1", "fromAccountType": "MAIN"},
        "GET /api/v1/earn/redeem-preview",
        query={"orderId": "1", "fromAccountType": "MAIN"},
    ),
    Case(
        "redeem_earn",
        {"orderId": "1", "amount": "10"},
        "DELETE /api/v1/earn/orders",
        query={"orderId": "1", "amount": "10"},
    ),
    Case(
        "get_earn_savings_products",
        {"currency": "USDT"},
        "GET /api/v1/earn/saving/products",
        query={"currency": "USDT"},
    ),
    Case("get_earn_promotion_products", {}, "GET /api/v1/earn/promotion/products"),
    Case("get_earn_staking_products", {}, "GET /api/v1/earn/staking/products"),
    Case("get_earn_kcs_staking_products", {}, "GET /api/v1/earn/kcs-staking/products"),
    Case("get_earn_eth_staking_products", {}, "GET /api/v1/earn/eth-staking/products"),
    Case("get_earn_account_holdings", {}, "GET /api/v1/earn/hold-assets"),
    Case(
        "get_dual_investment_products",
        {
            "category": "DUAL_CLASSIC",
            "strikeCurrency": "BTC",
            "investCurrency": "USDT",
            "side": "CALL",
        },
        "GET /api/v1/struct-earn/dual/products",
        query={"category": "DUAL_CLASSIC"},
    ),
    Case(
        "purchase_structured_earn",
        {
            "productId": "1",
            "investCurrency": "USDT",
            "investAmount": "10",
            "accountType": "MAIN",
        },
        "POST /api/v1/struct-earn/orders",
        body={"productId": "1", "investCurrency": "USDT"},
    ),
    Case(
        "get_structured_earn_orders",
        {"categories": "DUAL_CLASSIC"},
        "GET /api/v1/struct-earn/orders",
        query={"categories": "DUAL_CLASSIC"},
    ),
    # Margin (private).
    Case("get_cross_margin_account", {}, "GET /api/v3/margin/accounts"),
    Case("get_isolated_margin_account", {}, "GET /api/v3/isolated/accounts"),
    Case(
        "get_margin_borrow_interest_rate",
        {"currency": "USDT"},
        "GET /api/v3/margin/borrowRate",
        query={"currency": "USDT"},
    ),
    Case(
        "borrow_margin",
        {"currency": "USDT", "size": "10", "timeInForce": "IOC"},
        "POST /api/v3/margin/borrow",
        body={"currency": "USDT", "size": "10", "timeInForce": "IOC"},
    ),
    Case(
        "get_margin_borrow_history",
        {"currency": "USDT"},
        "GET /api/v3/margin/borrow",
        query={"currency": "USDT"},
    ),
    Case(
        "repay_margin",
        {"currency": "USDT", "size": "10"},
        "POST /api/v3/margin/repay",
        body={"currency": "USDT", "size": "10"},
    ),
    Case(
        "get_margin_repay_history",
        {"currency": "USDT"},
        "GET /api/v3/margin/repay",
        query={"currency": "USDT"},
    ),
    Case(
        "get_margin_interest_history",
        {"currency": "USDT", "product_symbol": SPOT},
        "GET /api/v3/margin/interest",
        query={"currency": "USDT", "symbol": "BTC-USDT"},
    ),
    Case(
        "modify_margin_leverage",
        {"leverage": "3"},
        "POST /api/v3/position/update-user-leverage",
        body={"leverage": "3"},
    ),
    Case(
        "get_margin_loan_market",
        {"currency": "USDT"},
        "GET /api/v3/project/list",
        query={"currency": "USDT"},
    ),
    Case(
        "purchase_margin_lending",
        {"currency": "USDT", "size": "10", "interestRate": "0.01"},
        "POST /api/v3/purchase",
        body={"currency": "USDT", "size": "10", "interestRate": "0.01"},
    ),
    Case(
        "modify_margin_lending_purchase",
        {"currency": "USDT", "purchaseOrderNo": "1", "interestRate": "0.01"},
        "POST /api/v3/lend/purchase/update",
        body={"currency": "USDT", "purchaseOrderNo": "1"},
    ),
    Case(
        "get_margin_lending_purchase_orders",
        {"status": "DONE", "currency": "USDT"},
        "GET /api/v3/purchase/orders",
        query={"status": "DONE", "currency": "USDT"},
    ),
    Case(
        "redeem_margin_lending",
        {"currency": "USDT", "size": "10", "purchaseOrderNo": "1"},
        "POST /api/v3/redeem",
        body={"currency": "USDT", "size": "10", "purchaseOrderNo": "1"},
    ),
    Case(
        "get_margin_lending_redeem_orders",
        {"status": "DONE", "currency": "USDT"},
        "GET /api/v3/redeem/orders",
        query={"status": "DONE", "currency": "USDT"},
    ),
    # Dead-man switch.
    Case(
        "set_dcp",
        {"timeout": 10, "symbols": ["BTC-USDT"]},
        "POST /api/v1/hf/orders/dead-cancel-all",
        body={"timeout": 10, "symbols": "BTC-USDT"},
    ),
    Case("get_dcp", {}, "GET /api/v1/hf/orders/dead-cancel-all/query"),
    # Spot HF orders.
    Case(
        "place_spot_order",
        {"product_symbol": SPOT, "side": "buy", "type_": "limit", **LIMIT},
        "POST /api/v1/hf/orders",
        body={"symbol": "BTC-USDT", "side": "buy", "type": "limit", "price": "100"},
    ),
    Case(
        "test_spot_order",
        {"product_symbol": SPOT, "side": "buy", "type_": "limit", **LIMIT},
        "POST /api/v1/hf/orders/test",
        body={"symbol": "BTC-USDT", "side": "buy", "type": "limit"},
    ),
    Case(
        "place_spot_market_order",
        {"product_symbol": SPOT, "side": "buy", "size": "1"},
        "POST /api/v1/hf/orders",
        body={"symbol": "BTC-USDT", "side": "buy", "type": "market"},
    ),
    Case(
        "place_spot_market_buy_order",
        {"product_symbol": SPOT, "funds": "10"},
        "POST /api/v1/hf/orders",
        body={"side": "buy", "type": "market", "funds": "10"},
    ),
    Case(
        "place_spot_market_sell_order",
        {"product_symbol": SPOT, "size": "1"},
        "POST /api/v1/hf/orders",
        body={"side": "sell", "type": "market"},
    ),
    Case(
        "place_spot_limit_order",
        {"product_symbol": SPOT, "side": "sell", **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "sell", "type": "limit"},
    ),
    Case(
        "place_spot_limit_buy_order",
        {"product_symbol": SPOT, **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "buy", "type": "limit"},
    ),
    Case(
        "place_spot_limit_sell_order",
        {"product_symbol": SPOT, **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "sell", "type": "limit"},
    ),
    Case(
        "place_spot_post_only_limit_order",
        {"product_symbol": SPOT, "side": "buy", **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "buy", "type": "limit", "postOnly": True},
    ),
    Case(
        "place_spot_post_only_limit_buy_order",
        {"product_symbol": SPOT, **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "buy", "type": "limit", "postOnly": True},
    ),
    Case(
        "place_spot_post_only_limit_sell_order",
        {"product_symbol": SPOT, **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "sell", "type": "limit", "postOnly": True},
    ),
    Case(
        "place_spot_batch_orders",
        {
            "orders": [
                {
                    "product_symbol": SPOT,
                    "side": "buy",
                    "type": "limit",
                    "size": "1",
                    "price": "100",
                }
            ]
        },
        "POST /api/v1/hf/orders/multi",
    ),
    Case(
        "place_spot_batch_limit_orders",
        {"orders": [{"product_symbol": SPOT, "side": "buy", "size": "1", "price": "100"}]},
        "POST /api/v1/hf/orders/multi",
    ),
    Case(
        "place_spot_batch_market_orders",
        {"orders": [{"product_symbol": SPOT, "side": "buy", "size": "1"}]},
        "POST /api/v1/hf/orders/multi",
    ),
    Case(
        "alter_spot_order",
        {"product_symbol": SPOT, "orderId": "1", "newPrice": "101"},
        "POST /api/v1/hf/orders/alter",
        body={"symbol": "BTC-USDT", "orderId": "1", "newPrice": "101"},
    ),
    Case(
        "cancel_spot_order",
        {"orderId": "abc", "product_symbol": SPOT},
        "DELETE /api/v1/hf/orders/abc",
        query={"symbol": "BTC-USDT"},
    ),
    Case(
        "cancel_spot_all_orders_by_symbol",
        {"product_symbol": SPOT},
        "DELETE /api/v1/hf/orders",
        query={"symbol": "BTC-USDT"},
    ),
    Case("cancel_spot_all_orders", {}, "DELETE /api/v1/hf/orders/cancelAll"),
    Case(
        "get_spot_open_orders",
        {"product_symbol": SPOT},
        "GET /api/v1/hf/orders/active/page",
        query={"symbol": "BTC-USDT"},
    ),
    Case(
        "get_spot_trade_history",
        {"product_symbol": SPOT},
        "GET /api/v1/hf/fills",
        query={"symbol": "BTC-USDT"},
    ),
    # Futures orders.
    Case(
        "place_futures_order",
        {"product_symbol": SWAP, "side": "buy", "type_": "limit", **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"symbol": "XBTUSDTM", "side": "buy", "type": "limit", "size": 1},
    ),
    Case(
        "test_futures_order",
        {"product_symbol": SWAP, "side": "buy", "type_": "limit", **FUT_LIMIT},
        "POST /api/v1/orders/test",
        host="futures",
        body={"symbol": "XBTUSDTM", "side": "buy"},
    ),
    Case(
        "place_futures_market_order",
        {"product_symbol": SWAP, "side": "buy", "size": "1", "leverage": 3},
        "POST /api/v1/orders",
        host="futures",
        body={"symbol": "XBTUSDTM", "side": "buy", "type": "market"},
    ),
    Case(
        "place_futures_market_buy_order",
        {"product_symbol": SWAP, "size": "1", "leverage": 3},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "buy", "type": "market"},
    ),
    Case(
        "place_futures_market_sell_order",
        {"product_symbol": SWAP, "size": "1", "leverage": 3},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "sell", "type": "market"},
    ),
    Case(
        "place_futures_limit_order",
        {"product_symbol": SWAP, "side": "sell", **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "sell", "type": "limit", "price": "100"},
    ),
    Case(
        "place_futures_limit_buy_order",
        {"product_symbol": SWAP, **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "buy", "type": "limit"},
    ),
    Case(
        "place_futures_limit_sell_order",
        {"product_symbol": SWAP, **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "sell", "type": "limit"},
    ),
    Case(
        "place_futures_post_only_limit_order",
        {"product_symbol": SWAP, "side": "buy", **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "buy", "type": "limit", "postOnly": True},
    ),
    Case(
        "place_futures_post_only_limit_buy_order",
        {"product_symbol": SWAP, **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "buy", "postOnly": True},
    ),
    Case(
        "place_futures_post_only_limit_sell_order",
        {"product_symbol": SWAP, **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "sell", "postOnly": True},
    ),
    Case(
        "get_futures_order_list",
        {"status": "active"},
        "GET /api/v1/orders",
        host="futures",
        query={"status": "active"},
    ),
    Case(
        "get_futures_order",
        {"orderId": "abc"},
        "GET /api/v1/orders/abc",
        host="futures",
    ),
    Case(
        "get_futures_order_by_client_oid",
        {"clientOid": "cid"},
        "GET /api/v1/orders/byClientOid",
        host="futures",
        query={"clientOid": "cid"},
    ),
    Case(
        "cancel_futures_order",
        {"orderId": "abc"},
        "DELETE /api/v1/orders/abc",
        host="futures",
    ),
    Case(
        "cancel_futures_order_by_client_oid",
        {"clientOid": "cid", "product_symbol": SWAP},
        "DELETE /api/v1/orders/client-order/cid",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "cancel_futures_all_orders",
        {"product_symbol": SWAP},
        "DELETE /api/v3/orders",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_futures_open_order_value",
        {"product_symbol": SWAP},
        "GET /api/v1/openOrderStatistics",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_futures_trade_history",
        {"product_symbol": SWAP},
        "GET /api/v1/fills",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_futures_recent_trade_history",
        {"product_symbol": SWAP},
        "GET /api/v1/recentFills",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    # UTA orders.
    Case(
        "place_uta_order",
        {
            "trade_type": "SPOT",
            "product_symbol": SPOT,
            "side": "BUY",
            "order_type": "LIMIT",
            "size": "1",
            "size_unit": "BASECCY",
            "price": "100",
            "time_in_force": "GTT",
            "cancel_after": 60,
            "stp": "CN",
        },
        "POST /api/ua/v2/unified/order/place",
        body={
            "tradeType": "SPOT",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "LIMIT",
            "sizeUnit": "BASECCY",
            "cancelAfter": 60,
            "stp": "CN",
        },
    ),
    Case(
        "cancel_uta_order",
        {"trade_type": "SPOT", "product_symbol": SPOT, "order_id": "1"},
        "POST /api/ua/v2/unified/order/cancel",
        body={"tradeType": "SPOT", "symbol": "BTC-USDT", "orderId": "1"},
    ),
    Case(
        "amend_uta_order",
        {
            "product_symbol": SWAP,
            "order_id": "1",
            "new_price": "101",
            "size_unit": "UNIT",
            "cxl_on_fail": True,
            "tp_trigger_price": "120",
            "sl_trigger_price": "80",
            "sl_trigger_price_type": "MP",
        },
        "POST /api/ua/v2/unified/order/amend",
        body={
            "symbol": "XBTUSDTM",
            "orderId": "1",
            "newPrice": "101",
            "sizeUnit": "UNIT",
            "cxlOnFail": True,
            "tpTriggerPrice": "120",
            "slTriggerPrice": "80",
            "slTriggerPriceType": "MP",
        },
    ),
    Case(
        "get_uta_order_detail",
        {"trade_type": "SPOT", "product_symbol": SPOT, "order_id": "1"},
        "GET /api/ua/v2/unified/order/detail",
        query={"tradeType": "SPOT", "symbol": "BTC-USDT", "orderId": "1"},
    ),
    Case(
        "get_uta_open_orders",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/unified/order/open-list",
        query={"tradeType": "SPOT"},
    ),
    Case(
        "get_uta_order_history",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/unified/order/history",
        query={"tradeType": "SPOT"},
    ),
    Case(
        "get_uta_trade_history",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/unified/order/execution",
        query={"tradeType": "SPOT"},
    ),
)


def _params(cases: tuple[Case, ...]) -> list[Any]:
    return [pytest.param(case, id=case.id) for case in cases]


@contextmanager
def _capture_server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    payload = json.dumps({"code": "200000", "data": {}}).encode()

    class Handler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            received.put(
                {
                    "method": self.command,
                    "path": self.path,
                    "headers": {key.lower(): value for key, value in self.headers.items()},
                    "body": self.rfile.read(length).decode() if length else "",
                }
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = _handle  # noqa: N815

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _client_kwargs(spot_url: str, futures_url: str) -> dict[str, Any]:
    return {
        "api_key": "api-key",
        "api_secret": "api-secret",
        "passphrase": "passphrase",
        "base_url": spot_url,
        "futures_base_url": futures_url,
        "preload_product_table": False,
        "timeout": 5,
    }


def _assert_request(
    case: Case,
    spot: queue.Queue[dict[str, Any]],
    futures: queue.Queue[dict[str, Any]],
) -> None:
    target, other = (spot, futures) if case.host == "spot" else (futures, spot)
    assert other.empty(), f"{case.method_name} was sent to the wrong KuCoin host"
    request = target.get_nowait()
    assert target.empty(), f"{case.method_name} sent more than one request"

    method, path = case.route.split(" ", 1)
    parts = urlsplit(request["path"])
    assert (request["method"], parts.path) == (method, path)
    query = dict(parse_qsl(parts.query))
    for key, value in case.query.items():
        assert query.get(key) == value, f"{case.method_name} query {query!r}"

    if case.body:
        body = json.loads(request["body"])
        for key, value in case.body.items():
            assert body.get(key) == value, f"{case.method_name} body {body!r}"
    elif method == "POST":
        assert isinstance(json.loads(request["body"]), dict | list)

    headers = request["headers"]
    if case.signed:
        assert headers.get("kc-api-key") == "api-key"
        assert headers.get("kc-api-sign")
        assert headers.get("kc-api-key-version") == "2"
    else:
        assert "kc-api-sign" not in headers


def _skip_if_native_is_stale(exc: ValueError, case: Case) -> None:
    """Skip when the installed ``dcex._native`` build predates this dispatch name."""
    message = str(exc)
    if "unsupported KuCoin" in message and "method" in message:
        pytest.skip(
            f"installed dcex._native does not know {case.method_name!r}; "
            "rebuild the extension (maturin develop) to exercise it"
        )
    raise exc


def _wrapper_names(mode: str) -> set[str]:
    base = ROOT / "dcex" / ("async_support" if mode == "async" else "") / "kucoin"
    module = "dcex.async_support.kucoin.client" if mode == "async" else "dcex.kucoin.client"
    client_cls = __import__(module, fromlist=["Client"]).Client
    names: set[str] = set()
    for path in base.glob("_*_http.py"):
        if path.name == "_http_manager.py":
            continue
        for name, member in inspect.getmembers(client_cls, inspect.isfunction):
            if name.startswith("_") or name in {"close", "async_init"}:
                continue
            if inspect.getsourcefile(member) == str(path):
                names.add(name)
    return names


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_every_kucoin_wrapper_has_a_route_case(mode: str) -> None:
    covered = {case.method_name for case in CASES}
    missing = _wrapper_names(mode) - covered
    assert not missing, f"add route cases for: {sorted(missing)}"


@pytest.mark.parametrize("case", _params(CASES))
def test_sync_kucoin_wrapper_hits_documented_route(case: Case) -> None:
    from dcex.kucoin.client import Client

    with _capture_server() as (spot_url, spot), _capture_server() as (futures_url, futures):
        client = Client(**_client_kwargs(spot_url, futures_url))
        try:
            result = getattr(client, case.method_name)(**case.kwargs)
        except ValueError as exc:
            _skip_if_native_is_stale(exc, case)
        finally:
            client.close()
        assert result == {"code": "200000", "data": {}}
        _assert_request(case, spot, futures)


@pytest.mark.asyncio
@pytest.mark.parametrize("case", _params(CASES))
async def test_async_kucoin_wrapper_hits_documented_route(case: Case) -> None:
    from dcex.async_support.kucoin.client import Client

    with _capture_server() as (spot_url, spot), _capture_server() as (futures_url, futures):
        client = Client(**_client_kwargs(spot_url, futures_url))
        await client.async_init()
        try:
            result = await getattr(client, case.method_name)(**case.kwargs)
        except ValueError as exc:
            _skip_if_native_is_stale(exc, case)
        finally:
            await client.close()
        assert result == {"code": "200000", "data": {}}
        _assert_request(case, spot, futures)


def test_set_dcp_sends_documented_symbols_field() -> None:
    from dcex.kucoin.client import Client

    with _capture_server() as (spot_url, spot), _capture_server() as (futures_url, _futures):
        client = Client(**_client_kwargs(spot_url, futures_url))
        try:
            client.set_dcp(timeout=10, symbols=["BTC-USDT", "ETH-USDT"])
            client.set_dcp(timeout=-1)
        finally:
            client.close()
        armed = json.loads(spot.get_nowait()["body"])
        unset = json.loads(spot.get_nowait()["body"])
    assert armed == {"timeout": 10, "symbols": "BTC-USDT,ETH-USDT"}
    assert unset == {"timeout": -1}


def test_uta_amend_rejects_spot_symbol_and_place_requires_size_unit() -> None:
    from dcex.kucoin.client import Client

    client = Client(**_client_kwargs("http://127.0.0.1:9", "http://127.0.0.1:9"))
    try:
        with pytest.raises(ValueError, match="futures only"):
            client.amend_uta_order(SPOT, order_id="1", new_price="101")
        with pytest.raises(TypeError, match="size_unit"):
            client.place_uta_order("SPOT", SPOT, "BUY", "MARKET", "1")  # type: ignore[call-arg]
    finally:
        client.close()
