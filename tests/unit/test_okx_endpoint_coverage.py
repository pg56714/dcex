"""
End-to-end offline coverage for every OKX REST wrapper.

Each public wrapper on the sync and async OKX clients is driven through the
real native extension against a local HTTP server, and the resulting HTTP
method, path, signing mode and key parameters are checked against the official
OKX v5 routes. This complements the auto-generated wrapper tests (which stub
the native client) and also covers ``_finance_http.py`` and
``_subaccount_http.py``, which are outside ``ENDPOINT_FILE_SUFFIXES``.
"""
# ruff: noqa: D101, D103, ANN401

from __future__ import annotations

import ast
import json
import queue
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
SPRD = "BTC-USDT_BTC-USDT-SWAP"
SWAP = "BTC-USDT-SWAP"


@dataclass(frozen=True)
class Case:
    name: str
    method: str
    path: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    signed: bool = True
    query: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)


def pub(
    name: str, path: str, *args: Any, query: dict[str, str] | None = None, **kwargs: Any
) -> Case:
    return Case(name, "GET", path, args, kwargs, signed=False, query=query or {})


def get(
    name: str, path: str, *args: Any, query: dict[str, str] | None = None, **kwargs: Any
) -> Case:
    return Case(name, "GET", path, args, kwargs, query=query or {})


def post(
    name: str, path: str, *args: Any, body: dict[str, Any] | None = None, **kwargs: Any
) -> Case:
    return Case(name, "POST", path, args, kwargs, body=body or {})


CASES: tuple[Case, ...] = (
    # Market data.
    pub(
        "get_candles_ticks",
        "/api/v5/market/candles",
        SWAP,
        bar="1m",
        query={"instId": SWAP, "bar": "1m"},
    ),
    pub("get_orderbook", "/api/v5/market/books", SWAP, sz="5", query={"instId": SWAP, "sz": "5"}),
    pub("get_tickers", "/api/v5/market/tickers", "SWAP", query={"instType": "SWAP"}),
    pub(
        "get_public_trades", "/api/v5/market/trades", "BTC-USDT-SPOT", query={"instId": "BTC-USDT"}
    ),
    pub("get_option_family_trades", "/api/v5/market/option/instrument-family-trades", "BTC-USD"),
    # Public data.
    pub("get_public_instruments", "/api/v5/public/instruments", "SPOT", query={"instType": "SPOT"}),
    pub("get_public_underlying", "/api/v5/public/underlying", "SWAP"),
    pub("get_funding_rate", "/api/v5/public/funding-rate", SWAP, query={"instId": SWAP}),
    pub("get_funding_rate_history", "/api/v5/public/funding-rate-history", SWAP, limit=5),
    pub("get_open_interest", "/api/v5/public/open-interest", "SWAP"),
    pub(
        "get_position_tiers",
        "/api/v5/public/position-tiers",
        "SWAP",
        "cross",
        product_symbol=SWAP,
        query={"instType": "SWAP", "tdMode": "cross", "instFamily": "BTC-USDT"},
    ),
    pub("get_trading_data_support_coin", "/api/v5/rubik/stat/trading-data/support-coin"),
    pub("get_taker_volume", "/api/v5/rubik/stat/taker-volume", "BTC", "SPOT"),
    pub("get_contract_taker_volume", "/api/v5/rubik/stat/taker-volume-contract", SWAP),
    pub("get_long_short_ratio", "/api/v5/rubik/stat/contracts/long-short-account-ratio", "BTC"),
    pub(
        "get_contract_long_short_ratio",
        "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract",
        SWAP,
    ),
    pub(
        "get_top_trader_long_short_account_ratio",
        "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader",
        SWAP,
    ),
    pub(
        "get_top_trader_long_short_position_ratio",
        "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader",
        SWAP,
    ),
    pub(
        "get_contracts_open_interest_and_volume",
        "/api/v5/rubik/stat/contracts/open-interest-volume",
        "BTC",
    ),
    pub(
        "get_contract_open_interest_history",
        "/api/v5/rubik/stat/contracts/open-interest-history",
        SWAP,
    ),
    pub(
        "get_delivery_exercise_history",
        "/api/v5/public/delivery-exercise-history",
        "OPTION",
        instFamily="BTC-USD",
    ),
    pub("get_option_summary", "/api/v5/public/opt-summary", instFamily="BTC-USD"),
    pub("get_option_tick_bands", "/api/v5/public/instrument-tick-bands", "OPTION"),
    pub("get_option_trades", "/api/v5/public/option-trades", instFamily="BTC-USD"),
    pub(
        "get_options_open_interest_and_volume",
        "/api/v5/rubik/stat/option/open-interest-volume",
        "BTC",
    ),
    pub("get_option_put_call_ratio", "/api/v5/rubik/stat/option/open-interest-volume-ratio", "BTC"),
    pub(
        "get_option_open_interest_and_volume_by_expiry",
        "/api/v5/rubik/stat/option/open-interest-volume-expiry",
        "BTC",
    ),
    pub(
        "get_option_open_interest_and_volume_by_strike",
        "/api/v5/rubik/stat/option/open-interest-volume-strike",
        "BTC",
        "20261225",
    ),
    pub("get_option_taker_block_volume", "/api/v5/rubik/stat/option/taker-block-volume", "BTC"),
    # Spread public data.
    pub("get_spread_spreads", "/api/v5/sprd/spreads", base_ccy="BTC", query={"baseCcy": "BTC"}),
    pub(
        "get_spread_books", "/api/v5/sprd/books", SPRD, depth="5", query={"sprdId": SPRD, "sz": "5"}
    ),
    pub("get_spread_ticker", "/api/v5/market/sprd-ticker", SPRD),
    pub("get_spread_candles", "/api/v5/market/sprd-candles", SPRD, bar="1m"),
    pub("get_spread_history_candles", "/api/v5/market/sprd-history-candles", SPRD, bar="1m"),
    pub("get_spread_public_trades", "/api/v5/sprd/public-trades", SPRD),
    # Trade.
    post(
        "place_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "buy",
        "limit",
        "1",
        px="100",
        clOrdId="c1",
        reduceOnly=True,
        body={"instId": SWAP, "side": "buy", "ordType": "limit", "px": "100", "reduceOnly": True},
    ),
    post(
        "place_batch_orders",
        "/api/v5/trade/batch-orders",
        [
            {
                "instId": SWAP,
                "tdMode": "cross",
                "side": "buy",
                "ordType": "limit",
                "sz": "1",
                "px": "1",
            }
        ],
    ),
    post(
        "place_market_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "sell",
        "1",
        body={"ordType": "market"},
    ),
    post(
        "place_market_buy_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        body={"ordType": "market", "side": "buy"},
    ),
    post(
        "place_market_sell_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        body={"ordType": "market", "side": "sell"},
    ),
    post(
        "place_limit_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "buy",
        "1",
        "10",
        body={"ordType": "limit"},
    ),
    post(
        "place_limit_buy_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        "10",
        body={"ordType": "limit", "side": "buy"},
    ),
    post(
        "place_limit_sell_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        "10",
        body={"ordType": "limit", "side": "sell"},
    ),
    post(
        "place_post_only_limit_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "buy",
        "1",
        "10",
        body={"ordType": "post_only"},
    ),
    post(
        "place_post_only_limit_buy_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        "10",
        body={"ordType": "post_only", "side": "buy"},
    ),
    post(
        "place_post_only_limit_sell_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        "10",
        body={"ordType": "post_only", "side": "sell"},
    ),
    post(
        "pre_check_order",
        "/api/v5/trade/order-precheck",
        SWAP,
        "cross",
        "buy",
        "limit",
        "1",
        body={"instId": SWAP},
    ),
    post(
        "cancel_order",
        "/api/v5/trade/cancel-order",
        SWAP,
        ordId="1",
        body={"instId": SWAP, "ordId": "1"},
    ),
    post(
        "cancel_batch_orders", "/api/v5/trade/cancel-batch-orders", [{"instId": SWAP, "ordId": "1"}]
    ),
    # With no pending orders the native helper only lists and returns.
    get(
        "cancel_all_orders",
        "/api/v5/trade/orders-pending",
        SWAP,
        query={"instId": SWAP, "limit": "100"},
    ),
    post(
        "amend_order",
        "/api/v5/trade/amend-order",
        SWAP,
        ordId="1",
        newPx="11",
        body={"instId": SWAP, "ordId": "1", "newPx": "11"},
    ),
    post(
        "amend_multiple_orders",
        "/api/v5/trade/amend-batch-orders",
        [{"instId": SWAP, "ordId": "1", "newSz": "2"}],
    ),
    post(
        "close_positions",
        "/api/v5/trade/close-position",
        SWAP,
        "cross",
        autoCxl=True,
        body={"instId": SWAP, "mgnMode": "cross", "autoCxl": True},
    ),
    get("get_order", "/api/v5/trade/order", SWAP, ordId="1", query={"instId": SWAP, "ordId": "1"}),
    get("get_order_list", "/api/v5/trade/orders-pending", "SWAP", query={"instType": "SWAP"}),
    get("get_orders_history", "/api/v5/trade/orders-history", "SWAP", query={"instType": "SWAP"}),
    get("get_orders_history_archive", "/api/v5/trade/orders-history-archive", "SWAP"),
    get("get_fills", "/api/v5/trade/fills", "SWAP"),
    get("get_fills_history", "/api/v5/trade/fills-history", "SWAP"),
    get("get_account_rate_limit", "/api/v5/trade/account-rate-limit"),
    post("set_cancel_all_after", "/api/v5/trade/cancel-all-after", "30", body={"timeOut": "30"}),
    get("get_easy_convert_currencies", "/api/v5/trade/easy-convert-currency-list"),
    get("get_easy_convert_history", "/api/v5/trade/easy-convert-history"),
    post(
        "place_easy_convert",
        "/api/v5/trade/easy-convert",
        ["ADA"],
        "USDT",
        body={"fromCcy": ["ADA"], "toCcy": "USDT"},
    ),
    # Spread trading.
    post(
        "place_spread_order",
        "/api/v5/sprd/order",
        SPRD,
        "buy",
        "limit",
        "1",
        price="2",
        body={"sprdId": SPRD, "px": "2", "sz": "1"},
    ),
    post("cancel_spread_order", "/api/v5/sprd/cancel-order", order_id="1", body={"ordId": "1"}),
    post("cancel_all_spread_orders", "/api/v5/sprd/mass-cancel", SPRD),
    get("get_spread_order", "/api/v5/sprd/order", order_id="1", query={"ordId": "1"}),
    get("get_spread_orders_pending", "/api/v5/sprd/orders-pending"),
    get("get_spread_orders_history", "/api/v5/sprd/orders-history"),
    post(
        "set_spread_cancel_all_after", "/api/v5/sprd/cancel-all-after", "10", body={"timeOut": "10"}
    ),
    get("get_spread_trades", "/api/v5/sprd/trades"),
    # Trading account.
    get("get_account_instruments", "/api/v5/account/instruments", "SWAP"),
    get("get_account_balance", "/api/v5/account/balance", "BTC", query={"ccy": "BTC"}),
    get("get_positions", "/api/v5/account/positions", "SWAP"),
    get("get_positions_history", "/api/v5/account/positions-history", "SWAP"),
    get("get_position_risk", "/api/v5/account/account-position-risk", "SWAP"),
    get("get_account_bills", "/api/v5/account/bills", "SWAP"),
    get("get_account_bills_archive", "/api/v5/account/bills-archive", "SWAP"),
    get("get_account_bills_history_archive", "/api/v5/account/bills-history-archive", "2026", "Q1"),
    post(
        "post_account_bills_history_archive", "/api/v5/account/bills-history-archive", "2026", "Q1"
    ),
    get("get_account_config", "/api/v5/account/config"),
    post(
        "set_position_mode",
        "/api/v5/account/set-position-mode",
        "long_short_mode",
        body={"posMode": "long_short_mode"},
    ),
    post(
        "set_leverage",
        "/api/v5/account/set-leverage",
        "5",
        "cross",
        product_symbol=SWAP,
        body={"lever": "5", "mgnMode": "cross", "instId": SWAP},
    ),
    get(
        "get_max_order_size",
        "/api/v5/account/max-size",
        SWAP,
        "cross",
        query={"instId": SWAP, "tdMode": "cross"},
    ),
    get("get_max_avail_size", "/api/v5/account/max-avail-size", SWAP, "cross"),
    get("get_leverage", "/api/v5/account/leverage-info", "cross", product_symbol=SWAP),
    get("get_adjust_leverage", "/api/v5/account/adjust-leverage-info", "SWAP", "cross", "3"),
    get("get_max_loan", "/api/v5/account/max-loan", "cross", product_symbol="BTC-USDT-SPOT"),
    get("get_spot_fee_rates", "/api/v5/account/trade-fee", query={"instType": "SPOT"}),
    get("get_margin_fee_rates", "/api/v5/account/trade-fee", query={"instType": "MARGIN"}),
    get("get_swap_fee_rates", "/api/v5/account/trade-fee", query={"instType": "SWAP"}),
    get("get_futures_fee_rates", "/api/v5/account/trade-fee", query={"instType": "FUTURES"}),
    get("get_option_fee_rates", "/api/v5/account/trade-fee", query={"instType": "OPTION"}),
    get("get_interest_accrued", "/api/v5/account/interest-accrued"),
    get("get_interest_rate", "/api/v5/account/interest-rate"),
    post("set_greeks", "/api/v5/account/set-greeks", "PA"),
    get("get_max_withdrawal", "/api/v5/account/max-withdrawal"),
    get("get_interest_limits", "/api/v5/account/interest-limits"),
    post(
        "spot_manual_borrow_repay",
        "/api/v5/account/spot-manual-borrow-repay",
        "USDT",
        "borrow",
        "1",
    ),
    post("set_spot_auto_repay", "/api/v5/account/set-auto-repay", True, body={"autoRepay": True}),
    get("get_spot_borrow_repay_history", "/api/v5/account/spot-borrow-repay-history"),
    # Funding account.
    get("get_currencies", "/api/v5/asset/currencies"),
    get("get_balances", "/api/v5/asset/balances"),
    get("get_asset_valuation", "/api/v5/asset/asset-valuation"),
    post(
        "funds_transfer",
        "/api/v5/asset/transfer",
        "USDT",
        "1",
        "FUND",
        "TRADING",
        body={"ccy": "USDT", "amt": "1", "from": "6", "to": "18"},
    ),
    get("get_transfer_state", "/api/v5/asset/transfer-state", "1"),
    get("get_bills", "/api/v5/asset/bills"),
    get("get_deposit_address", "/api/v5/asset/deposit-address", "USDT", query={"ccy": "USDT"}),
    get("get_deposit_history", "/api/v5/asset/deposit-history"),
    get(
        "get_deposit_withdraw_status",
        "/api/v5/asset/deposit-withdraw-status",
        "1",
        query={"wdId": "1"},
    ),
    get("get_exchange_list", "/api/v5/asset/exchange-list"),
    post("post_monthly_statement", "/api/v5/asset/monthly-statement", "Jan"),
    get("get_monthly_statement", "/api/v5/asset/monthly-statement", "Jan"),
    get("get_convert_currencies", "/api/v5/asset/convert/currencies"),
    get("get_convert_history", "/api/v5/asset/convert/history"),
    # Sub-account.
    get("get_subaccount_list", "/api/v5/users/subaccount/list"),
    get("get_subaccount_trading_balance", "/api/v5/account/subaccount/balances", "alpha"),
    get("get_subaccount_funding_balance", "/api/v5/asset/subaccount/balances", "alpha"),
    get("get_subaccount_bills", "/api/v5/asset/subaccount/bills", "alpha"),
    post(
        "transfer_between_subaccounts",
        "/api/v5/asset/subaccount/transfer",
        "USDT",
        "1",
        "FUND",
        "TRADING",
        "alpha",
        "beta",
        body={"from": "6", "to": "18", "fromSubAccount": "alpha", "toSubAccount": "beta"},
    ),
    get("get_entrusted_subaccount_list", "/api/v5/users/entrust-subaccount-list"),
    get("get_subaccount_interest_limits", "/api/v5/account/subaccount/interest-limits", "alpha"),
    # Financial products.
    get("get_saving_balance", "/api/v5/finance/savings/balance"),
    post(
        "purchase_redeem_savings",
        "/api/v5/finance/savings/purchase-redempt",
        "USDT",
        "1",
        "purchase",
    ),
    post("set_savings_lending_rate", "/api/v5/finance/savings/set-lending-rate", "USDT", "0.01"),
    get("get_savings_lending_history", "/api/v5/finance/savings/lending-history"),
    pub("get_public_borrow_info", "/api/v5/finance/savings/lending-rate-summary"),
    pub("get_public_borrow_history", "/api/v5/finance/savings/lending-rate-history"),
    post("set_auto_earn", "/api/v5/account/set-auto-earn", "USDT", "turn_on"),
    get("get_staking_offers", "/api/v5/finance/staking-defi/offers"),
    post(
        "purchase_staking",
        "/api/v5/finance/staking-defi/purchase",
        "p1",
        [{"ccy": "ETH", "amt": "1"}],
        body={"productId": "p1", "investData": [{"ccy": "ETH", "amt": "1"}]},
    ),
    post("redeem_staking", "/api/v5/finance/staking-defi/redeem", "o1", "defi"),
    post("cancel_staking", "/api/v5/finance/staking-defi/cancel", "o1", "defi"),
    get("get_active_staking_orders", "/api/v5/finance/staking-defi/orders-active"),
    get("get_staking_order_history", "/api/v5/finance/staking-defi/orders-history"),
    get("get_eth_staking_product_info", "/api/v5/finance/staking-defi/eth/product-info"),
    post("purchase_eth_staking", "/api/v5/finance/staking-defi/eth/purchase", "1"),
    post("redeem_eth_staking", "/api/v5/finance/staking-defi/eth/redeem", "1"),
    post("cancel_eth_staking_redemption", "/api/v5/finance/staking-defi/eth/cancel-redeem", "o1"),
    get("get_eth_staking_balance", "/api/v5/finance/staking-defi/eth/balance"),
    get(
        "get_eth_staking_history",
        "/api/v5/finance/staking-defi/eth/purchase-redeem-history",
        "purchase",
    ),
    pub(
        "get_eth_staking_apy_history",
        "/api/v5/finance/staking-defi/eth/apy-history",
        7,
        query={"days": "7"},
    ),
    get("get_sol_staking_product_info", "/api/v5/finance/staking-defi/sol/product-info"),
    post("purchase_sol_staking", "/api/v5/finance/staking-defi/sol/purchase", "1"),
    post("redeem_sol_staking", "/api/v5/finance/staking-defi/sol/redeem", "1"),
    get("get_sol_staking_balance", "/api/v5/finance/staking-defi/sol/balance"),
    get(
        "get_sol_staking_history",
        "/api/v5/finance/staking-defi/sol/purchase-redeem-history",
        "redeem",
    ),
    pub("get_sol_staking_apy_history", "/api/v5/finance/staking-defi/sol/apy-history", 7),
    get("get_flexible_loan_borrow_currencies", "/api/v5/finance/flexible-loan/borrow-currencies"),
    get("get_flexible_loan_collateral_assets", "/api/v5/finance/flexible-loan/collateral-assets"),
    post(
        "get_flexible_loan_max_loan",
        "/api/v5/finance/flexible-loan/max-loan",
        "USDT",
        [{"ccy": "BTC", "amt": "1"}],
    ),
    get(
        "get_flexible_loan_max_collateral_redeem",
        "/api/v5/finance/flexible-loan/max-collateral-redeem-amount",
        "BTC",
    ),
    post(
        "adjust_flexible_loan_collateral",
        "/api/v5/finance/flexible-loan/adjust-collateral",
        "add",
        "BTC",
        "1",
    ),
    get("get_flexible_loan_info", "/api/v5/finance/flexible-loan/loan-info"),
    get("get_flexible_loan_history", "/api/v5/finance/flexible-loan/loan-history"),
    get("get_flexible_loan_interest_accrued", "/api/v5/finance/flexible-loan/interest-accrued"),
    post(
        "borrow_flexible_loan",
        "/api/v5/finance/flexible-loan/borrow",
        [{"ccy": "USDT", "amt": "10"}],
        "c1",
    ),
    post("repay_flexible_loan", "/api/v5/finance/flexible-loan/repay", "o1", "USDT", "1", "c1"),
    get("get_flexible_loan_emode_info", "/api/v5/finance/flexible-loan/emode-info"),
    get("get_dual_investment_currency_pairs", "/api/v5/finance/sfp/dcd/currency-pair"),
    get("get_dual_investment_products", "/api/v5/finance/sfp/dcd/products", "BTC", "USDT", "C"),
    post("request_dual_investment_quote", "/api/v5/finance/sfp/dcd/quote", "p1", "10", "USDT"),
    post("trade_dual_investment", "/api/v5/finance/sfp/dcd/trade", "q1"),
    post("request_dual_investment_redeem_quote", "/api/v5/finance/sfp/dcd/redeem-quote", "o1"),
    post("redeem_dual_investment", "/api/v5/finance/sfp/dcd/redeem", "o1", "q1"),
    get("get_dual_investment_order_status", "/api/v5/finance/sfp/dcd/order-status", "o1"),
    get("get_dual_investment_order_history", "/api/v5/finance/sfp/dcd/order-history"),
    get("get_okusd_limits", "/api/v5/finance/okusd/limits"),
    get("get_okusd_account", "/api/v5/finance/okusd/account"),
    get("get_okusd_rate_history", "/api/v5/finance/okusd/rate/history"),
    get("get_okusd_subscribe_history", "/api/v5/finance/okusd/subscribe/history"),
    get("get_okusd_redeem_history", "/api/v5/finance/okusd/redeem/history"),
    get("get_okusd_rewards_history", "/api/v5/finance/okusd/rewards/history"),
    post("subscribe_okusd", "/api/v5/finance/okusd/subscribe", "10", "c1"),
    post("redeem_okusd", "/api/v5/finance/okusd/redeem", "10", "1", "c1"),
)

WRAPPER_FILES = (
    "_account_http.py",
    "_asset_http.py",
    "_finance_http.py",
    "_market_http.py",
    "_public_http.py",
    "_subaccount_http.py",
    "_trade_http.py",
)


class _Handler(BaseHTTPRequestHandler):
    received: queue.Queue[dict[str, Any]]

    def _handle(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode() if length else ""
        self.received.put(
            {
                "method": self.command,
                "path": self.path,
                "body": body,
                "signed": self.headers.get("OK-ACCESS-SIGN") is not None,
            }
        )
        payload = b'{"code":"0","msg":"","data":[]}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = _handle  # noqa: N815
    do_POST = _handle  # noqa: N815

    def log_message(self, _format: str, *_args: object) -> None:
        return


@pytest.fixture(scope="module")
def okx_server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    handler = type("Handler", (_Handler,), {"received": received})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "api_key": "key",
        "api_secret": "secret",
        "passphrase": "pass",
        "base_api": base_url,
        "timeout": 5,
        "preload_product_table": False,
    }


def _drain(received: queue.Queue[dict[str, Any]]) -> None:
    while not received.empty():
        received.get_nowait()


def _assert_request(case: Case, request: dict[str, Any]) -> None:
    split = urlsplit(request["path"])
    assert request["method"] == case.method, case.name
    assert split.path == case.path, case.name
    assert request["signed"] is case.signed, case.name
    query = dict(parse_qsl(split.query))
    for key, value in case.query.items():
        assert query.get(key) == value, (case.name, key, query)
    if case.method == "POST":
        body = json.loads(request["body"])
        for key, value in case.body.items():
            assert body.get(key) == value, (case.name, key, body)
    else:
        assert request["body"] == "", case.name


def _native_supports_spread() -> bool:
    """
    Return whether the installed native extension dispatches spread routes.

    Spread trading was added to the Rust sources after some local builds of
    ``dcex._native``; stale builds reject the method name before any network I/O.
    """
    import dcex._native as native

    client = native.OkxHttpClient(timeout=1, base_url="http://127.0.0.1:9")
    try:
        client.public_request_json("get_spread_books", [])
    except ValueError as error:
        return "unsupported OKX public method" not in str(error)
    except Exception:  # noqa: BLE001 - any transport error means the route exists
        return True
    return True


NATIVE_SUPPORTS_SPREAD = _native_supports_spread()


def _skip_if_stale_native(case: Case) -> None:
    if "spread" in case.name and not NATIVE_SUPPORTS_SPREAD:
        pytest.skip("installed dcex._native predates OKX spread routes; rebuild with maturin")


def _public_wrapper_names(base: Path) -> set[str]:
    names: set[str] = set()
    for file_name in WRAPPER_FILES:
        tree = ast.parse((base / file_name).read_text(encoding="utf-8"))
        for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            for node in cls.body:
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef)
                ) and not node.name.startswith("_"):
                    names.add(node.name)
    return names


def test_case_table_covers_every_sync_and_async_wrapper() -> None:
    case_names = [case.name for case in CASES]
    assert len(case_names) == len(set(case_names))
    sync_names = _public_wrapper_names(ROOT / "dcex" / "okx")
    async_names = _public_wrapper_names(ROOT / "dcex" / "async_support" / "okx")
    assert sync_names == async_names
    assert sync_names == set(case_names)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_sync_okx_wrapper_hits_official_route(
    case: Case, okx_server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    from dcex.okx.client import Client

    _skip_if_stale_native(case)
    base_url, received = okx_server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    result = getattr(client, case.name)(*case.args, **case.kwargs)
    assert result["code"] == "0"
    _assert_request(case, received.get(timeout=5))
    assert received.empty(), case.name


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
async def test_async_okx_wrapper_hits_official_route(
    case: Case, okx_server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    from dcex.async_support.okx.client import Client

    _skip_if_stale_native(case)
    base_url, received = okx_server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    await client.async_init()
    try:
        result = await getattr(client, case.name)(*case.args, **case.kwargs)
    finally:
        await client.close()
    assert result["code"] == "0"
    _assert_request(case, received.get(timeout=5))
    assert received.empty(), case.name


def test_sync_cancel_all_orders_batches_only_matching_pending_orders() -> None:
    """cancel_all_orders must list, filter by instrument, then batch-cancel."""
    from dcex.okx.client import Client

    pending = {
        "code": "0",
        "msg": "",
        "data": [
            {"instId": SWAP, "ordId": "1", "clOrdId": "a"},
            {"instId": "ETH-USDT-SWAP", "ordId": "2"},
            {"instId": SWAP, "ordId": "3"},
        ],
    }
    received: queue.Queue[dict[str, Any]] = queue.Queue()

    class Handler(_Handler):
        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode() if length else ""
            received.put({"method": self.command, "path": self.path, "body": body})
            payload = json.dumps(
                pending
                if self.command == "GET"
                else {"code": "0", "msg": "", "data": [{"sCode": "0"}]}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = _handle  # noqa: N815
        do_POST = _handle  # noqa: N815

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        client = Client(**_client_kwargs(f"http://{host}:{port}"))
        result = client.cancel_all_orders(SWAP)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    listing = received.get_nowait()
    cancel = received.get_nowait()
    assert received.empty()
    assert listing["method"] == "GET"
    assert urlsplit(listing["path"]).path == "/api/v5/trade/orders-pending"
    assert cancel["method"] == "POST"
    assert cancel["path"] == "/api/v5/trade/cancel-batch-orders"
    assert json.loads(cancel["body"]) == [
        {"instId": SWAP, "ordId": "1", "clOrdId": "a"},
        {"instId": SWAP, "ordId": "3"},
    ]
    assert result["data"] == [{"sCode": "0"}]


@pytest.mark.parametrize(
    ("module_path", "method_name"),
    [
        ("dcex.okx._finance_http:FinanceHTTP", "set_savings_lending_rate"),
        ("dcex.okx._subaccount_http:SubaccountHTTP", "get_subaccount_interest_limits"),
        ("dcex.async_support.okx._finance_http:FinanceHTTP", "set_savings_lending_rate"),
        (
            "dcex.async_support.okx._subaccount_http:SubaccountHTTP",
            "get_subaccount_interest_limits",
        ),
    ],
)
def test_undocumented_okx_wrappers_are_marked_deprecated(
    module_path: str, method_name: str
) -> None:
    import importlib

    module_name, class_name = module_path.split(":")
    method = getattr(getattr(importlib.import_module(module_name), class_name), method_name)
    assert method.__doc__ is not None
    assert "Deprecated" in method.__doc__
