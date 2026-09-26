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
        thread.join(timeout=5)


def _native_client(base_url: str) -> Any:
    return native.BybitHttpClient(
        api_key="api-key",
        api_secret="api-secret",
        recv_window=5000,
        sync_server_time=False,
        timeout=5,
        base_url=base_url,
    )


def _skip_if_native_is_stale(exc: ValueError) -> None:
    # The installed extension can lag the Rust source until it is rebuilt with maturin.
    if str(exc).startswith(("unsupported Bybit public method", "unsupported Bybit private method")):
        pytest.skip(f"installed dcex._native predates this route: {exc}")
    raise exc


def _assert_route(case: RouteCase, received: queue.Queue[dict[str, Any]]) -> None:
    assert received.qsize() == 1, f"{case.method_name} sent {received.qsize()} requests"
    request = received.get_nowait()
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


def _sync_client(base_url: str) -> Any:
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
            _skip_if_native_is_stale(exc)
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
            _skip_if_native_is_stale(exc)
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
    covered = {case.method_name for case in CASES}
    assert sorted(names - covered) == []
    assert sorted(covered - names) == []
